from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
import re
from model_utils.managers import InheritanceManager


ANSWER_ORDER_OPTIONS = (
    ('content', 'Content'),
    ('random', 'Random'),
    ('none', 'None'),
)

# Create your models here.

class CategoryManager(models.Manager):
    def new_category(self, category):
        new_category = self.create(category=re.sub('\s+', '-', category).lower())
        new_category.save()
        return new_category


class Category(models.Model):

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    category = models.CharField(
        verbose_name="Category",
        max_length=250,
        unique=True,
        blank=True,
        null=True,)

    objects = CategoryManager()

    def __str__(self):
        return self.category


class SubCategory(models.Model):

    class Meta:
        verbose_name = "Sub-Category"
        verbose_name_plural = "Sub-Categories"

    sub_category = models.CharField(
        verbose_name="Sub-Category",
        max_length=250,
        unique=False,
        blank=True,
    )
    category = models.ForeignKey(
        Category,
        null=True,
        blank=True,
        verbose_name="Category",
        on_delete=models.CASCADE,)

    objects = CategoryManager()

    def __str__(self):
        return self.sub_category + " (" + self.category.category + ")"

    def subcategory_name(self):
        return self.sub_category

class Quiz(models.Model):

    title = models.CharField(
        verbose_name="Title",
        max_length=60,
        blank=False,)

    description = models.TextField(
        verbose_name="Description",
        blank=True,
        help_text="A description of the quiz",)

    url = models.SlugField(
        verbose_name="User friendly URL",
        max_length=60,
        blank=False,
        unique=True,
        help_text="The URL of the quiz",)

    category = models.ForeignKey(
        Category,
        verbose_name="Category",
        null=True,
        blank=True,
        on_delete=models.CASCADE,)

    random_order = models.BooleanField(
        verbose_name="Random order",
        default=False,
        blank=False,
        null=False,
        help_text="Whether the quiz is randomly ordered or not",)

    max_questions = models.PositiveIntegerField(
        verbose_name="Max questions",
        blank=True,
        null=True,
        help_text="The maximum number of questions to show",)

    answers_at_end = models.BooleanField(
        verbose_name="Answers at end",
        default=False,
        blank=False,
        null=False,
        help_text="Show answers at end of quiz, not after each question",)

    exam_paper = models.BooleanField(
        verbose_name="Exam paper",
        default=False,
        blank=False,
        null=False,
        help_text="If yes, save quiz results for scoring",)

    single_attempt = models.BooleanField(
        verbose_name="Single attempt",
        default=False,
        blank=False,
        null=False,
        help_text="If yes, only one attempt permitted and non-users cannot take it",)

    pass_mark = models.SmallIntegerField(
        verbose_name="Pass mark",
        default=0,
        blank=True,
        validators=[MaxValueValidator(100), MinValueValidator(0)],
        help_text="Percent required to pass exam",)

    success_text = models.TextField(
        verbose_name="Success test",
        blank=True,
        help_text="Displayed if user passes exam",)

    fail_text = models.TextField(
        verbose_name="Fail text",
        blank=True,
        help_text="Displayed if user fails exam",)

    draft = models.BooleanField(
        verbose_name="Draft",
        default=False,
        blank=True,
        help_text="If yes, the quiz is not available to users",)

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        self.url = re.sub('\s+', '-', self.url).lower()

        self.url = ''.join(letter for letter in self.url if letter.isalnum() or letter == '-')

        if self.single_attempt is True:
            self.exam_paper = True

        if self.pass_mark > 100:
            raise ValidationError('%s is above 100' % self.pass_mark)

        super(Quiz, self).save(force_insert, force_update, *args, **kwargs)

    class Meta:
        verbose_name = "Quiz"
        verbose_name_plural = "Quizzes"

    def __str__(self):
        return self.title

    def get_questions(self):
        return self.question_set.all().select_subclasses()

    def set_questions(self, questions):
        self.question_set.set(questions)

    @property
    def get_max_score(self):
        return self.get_questions().count()

    def anon_score_id(self):
        return str(self.id) + "_score"

    def anon_q_list(self):
        return str(self.id) + "_q_list"

    def anon_q_data(self):
        return str(self.id) + "_data"


class Question(models.Model):
    quiz = models.ManyToManyField(
        Quiz,
        verbose_name="Quiz",
        blank=True,
    )

    category = models.ForeignKey(
        Category,
        verbose_name="Category",
        null=True,
        blank=True,
        on_delete=models.CASCADE, )

    sub_category = models.ForeignKey(
        SubCategory,
        verbose_name="Sub-Category",
        null=True,
        blank=True,
        on_delete=models.CASCADE, )

    figure = models.ImageField(
        upload_to="images",
        null=True,
        blank=True,
        verbose_name="Figure", )

    content = models.TextField(
        blank=False,
        null=False,
        verbose_name="Question",
        help_text="Enter the question text that you want displayed", )

    explanation = models.TextField(
        blank=True,
        null=True,
        verbose_name="Explanation",
        help_text="Explanation to be shown after the question has been answered",
    )

    objects = InheritanceManager()

    class Meta:
        verbose_name = "Question"
        verbose_name_plural = "Questions"
        ordering = ['category']

    def __str__(self):
        return self.content


class MCQuestion(Question):

    answer_order = models.CharField(
        verbose_name="Answer order",
        max_length=30,
        null=True,
        blank=True,
        choices=ANSWER_ORDER_OPTIONS,
        help_text="The order that answer options are displayed",)

    multianswer = models.BooleanField(
        verbose_name="Multiple Correct Answers",
        default=False,
        blank=False,
        help_text="If yes, the question has more than one correct answer.",)

    def check_if_correct(self, guess):
            answer = Answer.objects.get(id=guess)
            if answer.correct is True:
                return True
            else:
                return False

    def order_answers(self, queryset):
        if self.answer_order == 'content':
            return queryset.order_by('content')
        if self.answer_order == 'random':
            return queryset.order_by('?')
        if self.answer_order == 'none':
            return queryset.order_by()
        return queryset

    def get_answers(self):
        return self.order_answers(Answer.objects.filter(question=self))

    def get_answer_list(self):
        return [(answer.id, answer.content) for answer in self.order_answers(Answer.objects.filter(question=self))]

    def answer_choice_to_string(self, guess):
        return Answer.objects.get(id=guess).content

    class Meta:
        verbose_name = "Multiple Choice Question"
        verbose_name_plural = "Multiple Choice Questions"


class Answer(models.Model):

    question = models.ForeignKey(
        MCQuestion,
        verbose_name="Question",
        on_delete=models.CASCADE,)

    content = models.CharField(
        verbose_name="Answer content",
        max_length=1000,
        blank=False,
        null=False,
        help_text="Answer content to be displayed",)

    correct = models.BooleanField(
        verbose_name="Correct",
        default=False,
        blank=False,
        null=False,
        help_text="Is this answer correct?",)

    class Meta:
        verbose_name = "Answer"
        verbose_name_plural = "Answers"

    def __str__(self):
        return self.content