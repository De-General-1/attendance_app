from django.urls import path
from .views import (
    dashboard,
    login_view,
    logout_view,
    register,
    profile_view,
    edit_profile_view,
    timesheets,
    request_leave,
    employees,
    employee_details,
    requests,
    request_details,
    accept_request,
    decline_request
)

urlpatterns = [
    path("", dashboard, name="home"),
    path("login/", login_view, name="login"),
    path("register/", register, name="register"),
    path("logout/", logout_view, name="logout"),
    path('profile/my_profile/', profile_view, name="profile"),
    path('profile/my_profile/edit', edit_profile_view, name="edit_profile"),
    path('timesheets/', timesheets, name="timesheets"),
    path('request_leave/', request_leave, name="request_leave"),
    path('employees/', employees, name="employees"),
    path('employees/<str:pk>/details', employee_details, name="employee_details"),
    path('requests/', requests, name="requests"),
    path('requests/<str:pk>/', request_details, name="request_detail"),
    path('accept_request/', accept_request, name="accept_request"),
    path('decline_request/', decline_request, name="decline_request"),
]
