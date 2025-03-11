from django.urls import path
from . import views

# set the namespace
app_name = 'hms'



urlpatterns = [
    path('', views.home, name='hms_home'),
    path('login', views.login, name='hms_login'),
    path('signup', views.signup, name='hms_signup'),
    path('logout', views.logout, name='hms_logout'),
    path('account', views.account, name='hms_account'),
    path('edit', views.edit, name='hms_edit'),
    path('delete', views.delete, name='hms_delete'),
    path('success', views.success, name='hms_success'),
    path('hotel', views.hotel, name='hms_hotel'),
    path('booking', views.booking, name='hms_booking'),
    path('myBooking', views.myBooking, name='hms_myBooking'),
    path('profile', views.profile, name='hms_profile'),
]
