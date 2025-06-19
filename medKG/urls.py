from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login_view'),
    path('login', views.login, name='login'),
    path('regist', views.regist, name='regist'),
    path('question', views.question, name='question'),
    path('api/qa/', views.qa_api, name='qa_api'),
    path('register', views.register, name='register'),
    path('api/suggestions/', views.suggestions_api, name='suggestions_api'),

    path('main', views.main, name='main'),
    path('kngraph', views.kngraph, name='kngraph'),
]