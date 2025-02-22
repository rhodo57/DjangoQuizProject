from unicodedata import category

from django.contrib import admin
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple

from .models import Category, SubCategory, Quiz, Question, MCQuestion, Answer


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4

class QuizAdminForm(forms.ModelForm):
    """
    below is from
    stackoverflow.com/questions/11657682/django-admin-interface-using-horizontal-filter-with-inline-manytomany-field
    """
    class Meta:
        model = Quiz
        exclude = []

    questions = forms.ModelMultipleChoiceField(
        queryset=Question.objects.all().select_subclasses(),
        required=False,
        label="Questions",
        widget=FilteredSelectMultiple(
            verbose_name="Questions",
            is_stacked=False,
        )
    )

    def __init__(self, *args, **kwargs):
        super(QuizAdminForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['questions'].initial = self.instance.question_set.all().select_subclasses()

    def save(self, commit=True):
        quiz = super(QuizAdminForm, self).save(commit=False)
        quiz.save()
        quiz.question_set.set(self.cleaned_data['questions'])
        self.save_m2m()
        return quiz


class QuizAdmin(admin.ModelAdmin):
    form = QuizAdminForm
    list_display = ('title', 'category')
    list_filter = ('category',)
    search_fields = ('description', 'category__category')


class CategoryAdmin(admin.ModelAdmin):
    search_fields = ['category']


class SubCategoryAdmin(admin.ModelAdmin):
    search_fields = ['sub_category']
    list_display = ('sub_category', 'category')
    list_filter = ['category']

class MCQuestionAdmin(admin.ModelAdmin):
    list_display = ('content', 'category')
    list_filter = ['category']
    fields = ['content', 'category', 'sub_category', 'figure', 'quiz', 'explanation', 'answer_order', 'multianswer']
    search_fields = ('content', 'explanation')
    filter_horizontal = ['quiz']
    inlines = [AnswerInline]


# Register your models here.
admin.site.register(Category, CategoryAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
admin.site.register(Quiz, QuizAdmin)
admin.site.register(MCQuestion, MCQuestionAdmin)