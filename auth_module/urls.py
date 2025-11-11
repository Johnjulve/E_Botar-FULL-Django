from django.urls import path
from . import views

app_name = 'auth_module'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('api/courses/<int:department_id>/', views.get_courses_by_department, name='get_courses_by_department'),
    path('api/generate-student-id/', views.generate_student_id, name='generate_student_id'),
]
