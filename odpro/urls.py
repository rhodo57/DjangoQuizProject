from django.urls import path
from . import views
from .views import CategoriesListView, QuestionShow
from django.contrib.auth import views as auth_views
from .forms import EmailAuthenticationForm

app_name = 'odpro'

urlpatterns = [
    path('', views.index, name="index"),
    # HOME SCREEN

    path('odpro/', views.index, name="index"),
    # HOME SCREEN

    path("categories/", CategoriesListView.as_view(), name="categories"),
    # CATEGORY LIST

    path("category/<int:cat_id>/" , views.makequiz, name="makequiz"),

    path("question/<str:quiz_name>", QuestionShow.as_view(), name="question"),
    # QUESTION DISPLAY

    path("reset/", views.reset_session, name="reset"),
    # CLEAR SESSION DATA

    path('login/', auth_views.LoginView.as_view(authentication_form=EmailAuthenticationForm), name='login'),

    path('register/', views.register, name='register'),

    path('odprofile/', views.odprofile, name='odprofile'),
]