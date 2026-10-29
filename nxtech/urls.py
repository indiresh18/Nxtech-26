from django.urls import path
from . import views

urlpatterns = [
    path('', views.nxtech_home, name='nxtech_home'),
    path('signin/', views.signin_view, name='signin'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.signout_view, name='signout'),
    
    path('hackathon/register/', views.register_hackathon, name='register_hackathon'),
    path('failure-analysis/register/', views.register_failure_analysis, name='register_failure_analysis'),
    path('confirmation/<str:event_type>/<int:team_id>/', views.registration_confirmation, name='nxtech_confirmation'),
    path('hackathon/download-problem-statements/', views.download_hackathon_problem_statements, name='download_hackathon_problem_statements'),
]

