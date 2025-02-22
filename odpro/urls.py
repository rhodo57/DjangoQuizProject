from django.urls import path
from . import views
from .views import CategoriesListView, QuestionShow

app_name = 'odpro'

urlpatterns = [
    path('', views.index, name="index"),
    # HOME SCREEN

    path("categories/", CategoriesListView.as_view(), name="categories"),
    # CATEGORY LIST

    path("question/", QuestionShow.as_view(), name="question"),
    # QUESTION DISPLAY

path("reset/", views.reset_session, name="reset"),
    # CLEAR SESSION DATA

]