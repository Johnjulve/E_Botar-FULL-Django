from django.urls import path
from . import views

app_name = 'result_module'

urlpatterns = [
    # Results Dashboard
    path('', views.results_dashboard, name='results_dashboard'),
    
    # Election Results
    path('election/<int:election_id>/', views.election_results, name='election_results'),
    path('election/<int:election_id>/position/<int:position_id>/', views.position_results, name='position_results'),
    path('election/<int:election_id>/statistics/', views.results_statistics, name='results_statistics'),
    
    # Results Management (Staff Only)
    path('election/<int:election_id>/generate/', views.generate_results, name='generate_results'),
    path('election/<int:election_id>/chart/create/', views.create_chart, name='create_chart'),
    
    # Results Export
    path('election/<int:election_id>/export/', views.export_results, name='export_results'),
    
    # Results Comparison
    path('comparison/', views.results_comparison, name='results_comparison'),
    
    # API Endpoints
    path('api/election/<int:election_id>/', views.results_api, name='results_api'),
]
