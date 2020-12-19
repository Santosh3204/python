from django.urls import path, include
from django.contrib.auth import views as auth_views

from . import views
from mentee.views import *


app_name = 'users'

urlpatterns = [
    path('login/callback', UserLoginView.as_view(), name='google_login'),
    path('dashboard',DashboardView.as_view(),name='dashboard_page'),
    # path('home', views.home, name='home_page'),
    path('', views.index, name='index'),
    # path('login-login/',views.play),
    path('add_mentor_details', views.insert_mentor_data, name='add_mentor_details'),
    path('register_profile', UserProfileView.as_view()),
    path('fetch_mentor_profile',FetchMentorProfile.as_view(),name='fetch_mentor_profile'),
    path('image/<int:id>/', MentorView.as_view(), name="mentor_view"),
    path('create_mentor_schedule', Mentor_Schedule_API.as_view(), name="mentor_schedule"),
    path('topic/', Mentor_Topics_API.as_view()),
    path('fetch_schedule', Fetch_Mentor_Schedule_Api.as_view()),
    path('calendar', Mentor_Calender_API.as_view()),
    path('deactivate', Row_Deactivate_API.as_view()),
    path('order', Booking_121.as_view()),
    path('profile/', Mentor_Profile_API.as_view()),
    path('mentor_booked_schedule', Booked_Sessions.as_view()),
    #path('excel/', excel_to_table.as_view()),
    path('create_order/', Create_Order_API.as_view()),
    path('verify_sign/', RP_Sign_Verification.as_view()),
    path('booked_schedule/', Booked_Sessions.as_view()),
    path('search', Search_API.as_view()),
    path('career_profile/', Fetch_Session_Names_API.as_view()),
    path('mentor_details/', Mentor_Details_API.as_view()),
    path('coupon/', Coupon_API.as_view()),
    path('mentee_orders/', Mentee_My_Orders_API.as_view()),
    path('mentor_orders/', Mentor_My_Orders_API.as_view()),
    path('pay_history/', Mentor_Payment_History.as_view()),
    path('mentee_feedback/', Mentee_Feedback.as_view()),
    path('get_call_token',VoiceCalling.as_view()),
    path('disconnect_call',DisconnectCall.as_view()),
    path('wallet/', Wallet_API.as_view()),
    path('wallet_verify/', wallet_verification.as_view()),
    path('wallet_history/', wallet_history.as_view()),
    path('make_payment/', make_payment.as_view()),
    path('favourites/', favourite_mentors.as_view()),
    path('profile_page/', profile_page.as_view()),
    path('search_mentors/',FindMentors.as_view()),
    #path('rz_test/', Razorpay_test.as_view()),
    #path('pay_test/', Pay_test.as_view()),
    path('get_fav_mentors/', fetch_favourite_mentors.as_view()),


]

    

