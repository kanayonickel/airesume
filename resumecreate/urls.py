from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'resumecreate'  # For namespacing

urlpatterns = [
    # path('', views.home, name='index'),
    # path('admin/', views.admin_dashboard, name='admin_dashboard'),
    # path('admin/users/', views.admin_registered_users, name='admin_users'),
    # path('admin/resumes/', views.admin_submitted_resumes, name='admin_resumes'),
    # path('admin/resume/<int:resume_id>/', views.admin_resume_detail, name='admin_resume_detail'),
    # path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    # path('signup/', views.register, name='signup'),
    # path('login/', views.CustomLoginView.as_view(), name='login'),
    # path('generate-cv/', views.generate_cv, name='generate_cv'),
    # path('generate-cover/', views.generate_cover, name='generate_cover'),
    # path('history/', views.user_history, name='history'),
    # path('resume/<int:resume_id>/', views.resume_detail, name='resume_detail'),
    # path('reset-conversation/', views.reset_conversation, name='reset_conversation'),
    
      # Home/Landing page
    path('', views.home, name='index'),
    
    # Authentication
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.custom_logout, name='logout'),  # USE FUNCTION VIEW
    path('signup/', views.register, name='signup'),
    
    # Resume builder pages
    path('generate-cv/', views.generate_cv, name='generate_cv'),
    path('generate-cover/', views.generate_cover, name='generate_cover'),
    path('history/', views.user_history, name='history'),
    path('resume/<int:resume_id>/', views.resume_detail, name='resume_detail'),
    path('reset-conversation/', views.reset_conversation, name='reset_conversation'),  # NEW
    path('recommend-jobs/', views.recommend_jobs_view, name='recommend_jobs'),
    # path('export-cover-letter-pdf/', views.export_cover_letter_pdf, name='export_cover_letter_pdf'),
   
   # Export functionality
    path('export-resume/', views.export_resume, name='export_resume'),  # NEW
    path('export-cover-letter/', views.export_cover_letter, name='export_cover_letter'),
    
    
    # Admin pages
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', views.admin_registered_users, name='admin_users'),
    path('admin/resumes/', views.admin_submitted_resumes, name='admin_resumes'),
    
    # Singing Ayra Starr here
]