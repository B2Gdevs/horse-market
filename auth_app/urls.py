from django.urls import path

from auth_app.views import UserList, UserDetails, GroupList
app_name="auth_app"
urlpatterns = [
    path('', UserList.as_view()),
    path('<pk>/', UserDetails.as_view()),
    path('groups/', GroupList.as_view()),
]