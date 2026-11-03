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
    path('failure-analysis/select-statement/', views.select_failure_analysis_statement, name='select_failure_analysis_statement'),
    path('failure-analysis/download-statements/', views.download_fa_problem_statements, name='download_fa_problem_statements'),
    path('failure-analysis/download-sources/', views.download_fa_case_sources, name='download_fa_case_sources'),
    path('failure-analysis/download-papers/', views.download_fa_research_papers, name='download_fa_research_papers'),
]

