from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('project/<int:project_id>/', views.project_detail_view, name='project_detail'),
    path('project/<int:project_id>/chat/', views.chat_api_view, name='chat_api'),
    path('project/<int:project_id>/chat_page/', views.chat_view, name='chat'),
    path('', views.home_view, name='home'),
]
