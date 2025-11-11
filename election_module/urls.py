from django.urls import path
from django.shortcuts import redirect
from . import views

app_name = 'election_module'

urlpatterns = [
    # Election URLs
    path('', views.election_list, name='school_election_list'),
    path('<int:election_id>/', views.election_detail, name='school_election_detail'),
    path('previous/', views.past_election_winners, name='past_election_winners'),
    path('create/', views.election_create, name='election_create'),
    path('<int:election_id>/edit/', views.election_edit, name='election_edit'),
    path('delete/', views.election_delete, name='election_delete'),
    path('<int:election_id>/results/', lambda request, election_id: redirect(f'/voting/election/{election_id}/school-results/'), name='school_election_results'),
    
    # Position URLs
    path('positions/', views.position_list, name='position_list'),
    path('positions/create/', views.position_create, name='position_create'),
    path('positions/<int:position_id>/edit/', views.position_edit, name='position_edit'),
    path('positions/delete/', views.position_delete, name='position_delete'),
    # Election controls
    path('pause/', views.election_pause, name='election_pause'),
    path('resume/', views.election_resume, name='election_resume'),
    path('end-now/', views.election_end_now, name='election_end_now'),
    path('positions/<int:position_id>/associate/', views.associate_position_with_election, name='associate_position_with_election'),
    path('positions/fix-associations/', views.fix_position_associations, name='fix_position_associations'),
    
    # Party URLs
    path('parties/', views.party_list, name='party_list'),
    path('parties/create/', views.party_create, name='party_create'),
    path('parties/<int:party_id>/edit/', views.party_edit, name='party_edit'),
    
    # AJAX URLs
    path('update-position-order/', views.update_position_order, name='update_position_order'),
    path('update-positions-order/', views.update_positions_order, name='update_positions_order'),
]
