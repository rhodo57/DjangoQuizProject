import random

from django.core.exceptions import PermissionDenied
from django.http import QueryDict, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, FormView, DetailView
from odpro.models import Quiz, Category, Question
from odpro.forms import QuestionForm


# Create your views here.
# ####################################################
def index(request):
    context = {'page': 'index'}
    return render(request, 'odpro/index.html', context)

# ####################################################

class CategoriesListView(ListView):
    model = Category

# ####################################################

class QuizListView(ListView):
    model = Quiz

    def get_queryset(self):
        queryset = super(QuizListView, self).get_queryset()
        return queryset.filter(draft=False)

# ####################################################

class QuizDetailView(DetailView):
    model = Quiz
    slug_field = 'url'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.object.draft and not request.user.has_perm('odpro.change_quiz'):
            raise PermissionDenied

        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

# ####################################################

class ViewQuizListByCategory(ListView):
    model = Quiz
    template_name = 'odpro/view_quiz_category.html'

    # The dispatch method takes in the request and ultimately returns the response.
    # Normally, it returns a response by calling (ie, dispatching to) another method - like get().
    # But the key concept is that it's the entry point for requests and ultimately responsible for returning the response.
    # When a request url matches a url in your urls.py file, django passes that request to the view you specified.
    # The request can only be passed to callable functions. This is why when using class-based views, you use the as_view() method.
    # The as_view() method returns a function that can be called.
    # This function then creates an instance of the view class and calls it's dispatch() method.
    # The dispatch method then looks at the request and decides whether the GET or POST method of the view class should handle the request.
    # https://stackoverflow.com/questions/47808652/what-is-dispatch-used-for-in-django
    def dispatch(self, request, *args, **kwargs):
        self.category = get_object_or_404(Category, category=self.kwargs['category_name'])
        return super(ViewQuizListByCategory, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ViewQuizListByCategory, self).get_context_data(**kwargs)
        context['category'] = self.category
        return context

    def get_queryset(self):
        queryset = super(ViewQuizListByCategory, self).get_queryset()
        return queryset.filter(category=self.category, draft=False)


# ########################################################

class QuestionShow(FormView):
    """
    Attempt to just show random questions
    """
    form_class = QuestionForm
    template_name = 'odpro/question.html'
    result_template_name = 'odpro/result.html'
    success_url = reverse_lazy('question')


    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.quiz = get_object_or_404(Quiz, url='random')

    def dispatch(self, request, *args, **kwargs):
        # print("in dispatch")
        # ALL INCOMING REQUESTS GET ROUTED THROUGH HERE
        # self.request = request
        # self.quiz = get_object_or_404(Quiz, url='random')
        self.sitting = self.anon_load_sitting() # GET QUESTION LIST
        return super(QuestionShow, self).dispatch(request, *args, **kwargs)

    def get_form(self, *args, **kwargs):
        # print("in get_form")
        # GET FORM PRE-POPULATED WITH NEXT QUESTION
        self.question = self.anon_next_question() # SET NEXT QUESTION
        self.progress = self.anon_sitting_progress()
        form_class = self.form_class
        return form_class(**self.get_form_kwargs()) # GET CHOICE LIST FOR QUESTION

    def get_form_kwargs(self):
        # print("in get_form_kwargs")
        # OVERRIDE get_form_kwargs() TO PRE-POPULATE FROM WITH QUESTION
        kwargs = super().get_form_kwargs()
        choice_list = [x for x in self.question.get_answer_list()]
        multi = False
        if self.question.multianswer is True:
            multi = True
        return dict(kwargs, multi=multi, choices=choice_list)

    def form_valid(self, form):
        # print("in form_valid")
        # CALLED WHEN VALID INCOMING FORM DATA HAS BEEN POSTED
        # REDIRECTS TO THE success_url
        self.form_valid_anon(form) # SCORE ANSWER / SET PREVIOUS / UPDATE QUESTION LIST

        # IF QUESTION LIST IS EMPTY REDIRECT TO FINAL RESULT
        if not self.request.session[self.quiz.anon_q_list()]:
            return self.final_result_anon()

        self.request.POST = QueryDict() # CLEAR POST DATA
        return super(QuestionShow, self).get(self, self.request) # RETURN REQUEST W/O THE POST DATA
        # return super(QuestionShow, self).form_valid(form)


    def get_context_data(self, **kwargs):
        # print("in get_context_data")
        # USED BY CLASS-BASED VIEWS TO PREPARE DATA FOR RENDERING A TEMPLATE
        # USED WHEN DATA FROM >1 MODEL IS NEEDED
        context = super().get_context_data(**kwargs)
        context['question'] = self.question
        context['quiz'] = self.quiz
        if hasattr(self, 'previous'):
            context['previous'] = self.previous
        if hasattr(self, 'progress'):
            context['progress'] = self.progress
        return context

    def anon_load_sitting(self):
        # print("in anon_load_sitting")
        # RETURNS EXISTING QUESTION LIST IF IT EXISTS. IF NOT, REQUEST A NEW ONE
        if self.quiz.anon_q_list() in self.request.session:
            return self.request.session[self.quiz.anon_q_list()]
        else:
            return self.new_anon_quiz_session()

    def new_anon_quiz_session(self):
        # print("in new_anon_quiz_session")
        self.request.session.set_expiry(2628288) # expires in 1 month
        questions = self.quiz.get_questions()
        question_list = [question.id for question in questions]
        random.shuffle(question_list)

        if self.quiz.max_questions and (self.quiz.max_questions <= len(question_list)):
            question_list = question_list[:self.quiz.max_questions]

        # session list of questions
        self.request.session[self.quiz.anon_q_list()] = question_list

        #session score for anon users
        self.request.session[self.quiz.anon_score_id()] = 0

        # session list of question order and incorrect questions
        self.request.session[self.quiz.anon_q_data()] = {'incorrect_questions': [], 'order': question_list}

        return self.request.session[self.quiz.anon_q_list()]

    def anon_next_question(self):
        # print("in anon_next_question")
        next_question_id = self.request.session[self.quiz.anon_q_list()][0]
        return Question.objects.get_subclass(id=next_question_id)

    def anon_sitting_progress(self):
        # print("in anon_sitting_progress")
        total = len(self.request.session[self.quiz.anon_q_data()]['order'])
        answered = total - len(self.request.session[self.quiz.anon_q_list()])
        return answered, total

    def form_valid_anon(self, form):
        # print("IN FORM_VALID_ANON")
        # 'GUESS' IS THE ITEM THAT WAS SELECTED IN THE MCQUESTION
        guess = form.cleaned_data['answers']
        is_correct = self.question.check_if_correct(guess)

        if is_correct:
            self.request.session[self.quiz.anon_score_id()] += 1
            anon_session_score(self.request.session, 1, 1)
        else:
            anon_session_score(self.request.session, 0, 1)
            self.request.session[self.quiz.anon_q_data()]['incorrect_questions'].append(self.question.id)

        # self.previous = {}
        self.previous = {
            'previous_answer': guess,
            'previous_outcome': is_correct,
            'previous_question': self.question,
            'answers': self.question.get_answers(),
            'question_type': {self.question.__class__.__name__: True}
        }
        # POP QUESTION OFF LIST
        question_list = self.request.session[self.quiz.anon_q_list()]
        question_list.pop(0)
        self.request.session[self.quiz.anon_q_list()] = question_list

    def final_result_anon(self):
        score = self.request.session[self.quiz.anon_score_id()]
        q_order = self.request.session[self.quiz.anon_q_data()]['order']
        max_score = len(q_order)
        percent = int(round((float(score) / max_score) * 100))
        session, session_possible = anon_session_score(self.request.session)
        if score == 0: score = "0"

        incorrect_q_id = self.request.session[self.quiz.anon_q_data()]['incorrect_questions']
        incorrect_questions = self.quiz.question_set.filter(id__in=incorrect_q_id).select_subclasses()

        results = {
            'score': score,
            'max_score': max_score,
            'percent': percent,
            'session': session,
            'possible': session_possible,
            'quiz': self.quiz,
            'incorrect_questions': incorrect_questions,
        }

        del self.request.session[self.quiz.anon_q_list()]

        if self.quiz.answers_at_end:
            results['questions'] = sorted(
                self.quiz.question_set.filter(id__in=q_order).select_subclasses(),
                key=lambda q:q_order.index(q.id)
            )
        else:
            results['previous'] = self.previous

        del self.request.session[self.quiz.anon_q_data()]

        return render(self.request, 'odpro/result.html', results)


# ########################################################

def anon_session_score(session, to_add=0, possible=0):
    """
    Returns the session score for non-signed in users.
    If number passed in then add this to the running total and return session score.

    examples:
        anon_session_score(1, 1) will add 1 out of a possible 1
        anon_session_score(0, 2) will add 0 out of a possible 2
        x, y = anon_session_score() will return the session score without modification
    """
    if "session_score" not in session:
        session["session_score"], session["session_score_possible"] = 0, 0

    if possible > 0:
        session["session_score"] += to_add
        session["session_score_possible"] += possible

    return session["session_score"], session["session_score_possible"]

# ########################################################

def reset_session(request):
    request.session.flush()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
