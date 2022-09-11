from django.urls import path
from .views import (
  RegisterView,
  RetrieveUserView,
  SendFriendRequestView,
  AcceptFriendRequestView,
  RejectFriendRequestView,
  CancelFriendRequestView,
  RemoveFriendView,
  GetFriendsView,
  GetFriendRequestsSentView,
  GetFriendRequestsReceivedView
)


urlpatterns = [
  path('register', RegisterView.as_view()),
  path('me', RetrieveUserView.as_view()),
  path('send-friend-request', SendFriendRequestView.as_view()),
  path('accept-friend-request', AcceptFriendRequestView.as_view()),
  path('reject-friend-request', RejectFriendRequestView.as_view()),
  path('cancel-friend-request', CancelFriendRequestView.as_view()),
  path('remove-friend', RemoveFriendView.as_view()),
  path('get-friends', GetFriendsView.as_view()),
  path('get-friend-requests-sent', GetFriendRequestsSentView.as_view()),
  path('get-friend-requests-received', GetFriendRequestsReceivedView.as_view()),
]
