from django.urls import path
from . import views

urlpatterns = [
    # Public URLs
    path('', views.home, name='home'),
    path('register/', views.register_user, name='register_user'),
    path('login/user/', views.login_user, name='login_user'),
    path('login/admin/', views.login_admin, name='login_admin'),
    path('logout/', views.logout_view, name='logout'),
    
    # User URLs
    path('dashboard/user/', views.dashboard_user, name='dashboard_user'),
    path('book/', views.book_appointment, name='book_appointment'),
    path('my-appointments/', views.my_appointments, name='my_appointments'),
    path('reschedule/<int:appointment_id>/', views.reschedule_appointment, name='reschedule_appointment'),
    path('cancel/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
    
    # Staff/Admin URLs
    path('dashboard/staff/', views.dashboard_admin, name='dashboard_admin'),
    path('staff/all-appointments/', views.view_all_appointments, name='view_all_appointments'),
]