from django.urls import path
from django.shortcuts import redirect
from . import views

app_name = 'voting_module'

urlpatterns = [
    # Voting Dashboard (main voting page)
    path('', views.voting_dashboard, name='voting_dashboard'),
    
    # Voting URLs
    path('history/', views.voting_history, name='my_voting_history'),
    path('receipt/verify/', views.verify_receipt, name='verify_receipt'),
    
    # Election-specific voting
    path('election/<int:election_id>/', views.election_voting, name='election_voting'),
    path('election/<int:election_id>/view-ballot/', views.view_ballot_entry, name='view_ballot_entry'),
    path('election/<int:election_id>/submit/', views.submit_vote, name='submit_vote'),
    path('election/<int:election_id>/receipt/', views.vote_receipt, name='vote_receipt'),
    path('election/<int:election_id>/ballot/', views.vote_receipt, name='my_ballot'),
    
    # Staff-only URLs
    path('election/<int:election_id>/results/', views.election_results, name='election_results'),
    path('election/<int:election_id>/school-results/', views.election_results, name='school_election_results'),
    path('election/<int:election_id>/statistics/', views.voting_statistics, name='voting_statistics'),
    
    # Candidate application (redirect to candidate module)
    path('candidate-application/', lambda request: redirect('/candidates/applications/create/'), name='candidate_application'),
    
    # Admin redirects (for backward compatibility)
    path('administration-dashboard/', lambda request: redirect('/admin-ui/'), name='administration_dashboard'),
    path('admin-user-tools/', lambda request: redirect('/admin-ui/users/import/'), name='admin_user_tools'),
    path('admin-user-tools-download/<str:download_token>/', lambda request, download_token: redirect(f'/admin-ui/users/export/?token={download_token}'), name='admin_user_tools_download'),
    path('activity-logs/', lambda request: redirect('/admin-ui/activity-logs/'), name='activity_logs'),
    path('reset-user-password/<int:user_id>/', lambda request, user_id: redirect(f'/admin-ui/users/{user_id}/reset-password/'), name='reset_user_password'),
    
    # Election redirects (for backward compatibility)
    path('school-elections/', lambda request: redirect('/elections/'), name='school_election_list'),
    
    # Candidate redirects (for backward compatibility)
    path('my-applications/', lambda request: redirect('/candidates/applications/'), name='my_applications'),
    
    # Auth redirects (for backward compatibility)
    path('profile/', lambda request: redirect('/auth/profile/'), name='profile'),
]
