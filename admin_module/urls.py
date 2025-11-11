from django.urls import path
from django.shortcuts import redirect
from . import views
from election_module import views as election_views

app_name = 'admin_module'

urlpatterns = [
    # Dashboard
    path('', views.admin_dashboard, name='admin_dashboard'),
    
    # User Management
    path('users/', views.user_management, name='user_management'),
    path('users/create/', views.create_user, name='create_user'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('users/edit-ajax/', views.user_edit_ajax, name='user_edit_ajax'),
    path('users/<int:user_id>/reset-password/', views.reset_user_password, name='reset_user_password'),
    path('users/delete/', views.user_delete, name='user_delete'),
    path('users/import/', views.bulk_user_import, name='bulk_user_import'),
    path('users/generate/', views.bulk_user_generation, name='bulk_user_generation'),
    path('users/generate/results/', views.bulk_user_results, name='bulk_user_results'),
    path('users/export/', views.export_users, name='export_users'),
    path('users/autocomplete/', views.user_autocomplete, name='user_autocomplete'),
    
    # Election Management
    path('elections/', views.election_management, name='election_management'),
    path('elections/list/', views.elections_list, name='elections_list'),
    
    # Candidate Management
    path('candidates/', views.candidate_management, name='candidates_list'),
    path('candidates/create/', views.candidate_create, name='candidate_create'),
    path('candidates/<int:candidate_id>/edit/', views.candidate_edit, name='candidate_edit'),
    path('candidates/delete/', views.candidate_delete, name='candidate_delete'),
    path('review/', views.review_applications, name='review_applications'),
    path('applications/<int:application_id>/approve/', views.approve_application, name='approve_application'),
    path('applications/<int:application_id>/reject/', views.reject_application, name='reject_application'),
    
    # System Management
    path('activity-logs/', views.activity_logs, name='activity_logs'),
    path('statistics/', views.system_statistics, name='system_statistics'),
    
    # Analytics
    path('analytics/course/<int:election_id>/', views.course_analytics, name='course_analytics'),
    path('analytics/department/<int:election_id>/', views.department_analytics, name='department_analytics'),
    
    # Department Management
    path('departments/', views.department_management, name='department_management'),
    path('departments/create/', views.department_create, name='department_create'),
    path('departments/<int:department_id>/edit/', views.department_edit, name='department_edit'),
    path('departments/delete/', views.department_delete, name='department_delete'),
    path('departments/export-csv/', views.department_export_csv, name='department_export_csv'),
    path('departments/import-csv/', views.department_import_csv, name='department_import_csv'),
    
    # Course Management
    path('courses/', views.course_management, name='course_management'),
    path('courses/create/', views.course_create, name='course_create'),
    path('courses/<int:course_id>/edit/', views.course_edit, name='course_edit'),
    path('courses/delete/', views.course_delete, name='course_delete'),
    path('courses/export-csv/', views.course_export_csv, name='course_export_csv'),
    path('courses/import-csv/', views.course_import_csv, name='course_import_csv'),
    
    # Position Management (from election_module)
    path('positions/', election_views.position_list, name='positions_list'),
    path('positions/create/', election_views.position_create, name='position_create'),
    path('positions/<int:position_id>/edit/', election_views.position_edit, name='position_edit'),
    path('positions/delete/', election_views.position_delete, name='position_delete'),
    path('positions/<int:position_id>/associate/', election_views.associate_position_with_election, name='associate_position_with_election'),
    path('positions/fix-associations/', election_views.fix_position_associations, name='fix_position_associations'),
    path('positions/reorder/', election_views.update_positions_order, name='positions_reorder'),
    # Party Management (from election_module)
    path('parties/', election_views.party_list, name='parties_list'),
    path('parties/create/', election_views.party_create, name='party_create'),
    path('parties/<int:party_id>/edit/', election_views.party_edit, name='party_edit'),
]
