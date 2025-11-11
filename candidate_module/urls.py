from django.urls import path
from . import views

app_name = 'candidate_module'

urlpatterns = [
    # Candidate Dashboard
    path('dashboard/', views.candidate_dashboard, name='candidate_dashboard'),
    
    # Candidate Profile
    path('profile/', views.candidate_profile, name='candidate_profile'),
    path('profile/edit/', views.edit_candidate_profile, name='edit_candidate_profile'),
    path('candidate/<int:candidate_id>/', views.view_candidate_profile, name='view_candidate_profile'),
    # Applications
    path('apply/', views.create_application, name='candidate_application'),
    path('applications/', views.candidate_applications, name='my_applications'),
    path('applications/create/', views.create_application, name='create_application'),
    path('applications/<int:application_id>/edit/', views.edit_application, name='edit_application'),
    path('applications/<int:application_id>/delete/', views.delete_application, name='delete_application'),
    
    # Elections
    path('elections/', views.available_elections, name='available_elections'),
    path('elections/<int:election_id>/', views.election_detail, name='election_detail'),
]