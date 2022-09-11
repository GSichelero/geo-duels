from .models import FriendRequest
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from .serializers import FriendRequestSerializer, User, UserCreateSerializer, UserSerializer


class RegisterView(APIView):
  def post(self, request):
    data = request.data

    serializer = UserCreateSerializer(data=data)

    if not serializer.is_valid():
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user = serializer.create(serializer.validated_data)
    user = UserSerializer(user)

    return Response(user.data, status=status.HTTP_201_CREATED)


class RetrieveUserView(APIView):
  permission_classes = [permissions.IsAuthenticated]

  def get(self, request):
    user = request.user
    user = UserSerializer(user)

    return Response(user.data, status=status.HTTP_200_OK)


class SendFriendRequestView(APIView):
  permission_classes = [permissions.IsAuthenticated]

  def post(self, request):
    data = request.data
    to_user_id = data.get('to_user_id')

    if not to_user_id:
      return Response({'error': 'to_user_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    if to_user_id == str(request.user.id):
      return Response({'error': 'You cannot send friend request to yourself'}, status=status.HTTP_400_BAD_REQUEST)

    if request.user.friends.filter(id=to_user_id).exists():
      return Response({'error': 'You are already friends with this user'}, status=status.HTTP_400_BAD_REQUEST)

    if request.user.friend_requests_sent.filter(to_user_id=to_user_id).exists():
      return Response({'error': 'You have already sent a friend request to this user'}, status=status.HTTP_400_BAD_REQUEST)

    if request.user.friend_requests_received.filter(from_user_id=to_user_id).exists():
      return Response({'error': 'This user has already sent you a friend request'}, status=status.HTTP_400_BAD_REQUEST)

    friend_request = FriendRequest.objects.create(
      from_user=request.user,
      to_user_id=to_user_id,
    )

    return Response({'success': 'Friend request sent successfully'}, status=status.HTTP_200_OK)


class AcceptFriendRequestView(APIView):
  permission_classes = [permissions.IsAuthenticated]

  def post(self, request):
    data = request.data
    request_id = data.get('request_id')

    if not request_id:
      return Response({'error': 'request_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
      friend_request = FriendRequest.objects.get(id=request_id)
    except FriendRequest.DoesNotExist:
      return Response({'error': 'Friend request not found'}, status=status.HTTP_404_NOT_FOUND)

    if friend_request.to_user != request.user:
      return Response({'error': 'You are not allowed to accept this friend request'}, status=status.HTTP_400_BAD_REQUEST)

    request.user.friends.add(friend_request.from_user)
    friend_request.from_user.friends.add(request.user)

    friend_request.delete()

    return Response({'success': 'Friend request accepted successfully'}, status=status.HTTP_200_OK)


class RejectFriendRequestView(APIView):
  permission_classes = [permissions.IsAuthenticated]

  def post(self, request):
    data = request.data
    request_id = data.get('request_id')

    if not request_id:
      return Response({'error': 'request_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
      friend_request = FriendRequest.objects.get(id=request_id)
    except FriendRequest.DoesNotExist:
      return Response({'error': 'Friend request not found'}, status=status.HTTP_404_NOT_FOUND)

    if friend_request.to_user != request.user:
      return Response({'error': 'You are not allowed to reject this friend request'}, status=status.HTTP_400_BAD_REQUEST)

    friend_request.delete()

    return Response({'success': 'Friend request rejected successfully'}, status=status.HTTP_200_OK)


class CancelFriendRequestView(APIView):
  permission_classes = [permissions.IsAuthenticated]

  def post(self, request):
    data = request.data
    request_id = data.get('request_id')

    if not request_id:
      return Response({'error': 'request_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
      friend_request = FriendRequest.objects.get(id=request_id)
    except FriendRequest.DoesNotExist:
      return Response({'error': 'Friend request not found'}, status=status.HTTP_404_NOT_FOUND)

    if friend_request.from_user != request.user:
      return Response({'error': 'You are not allowed to cancel this friend request'}, status=status.HTTP_400_BAD_REQUEST)

    friend_request.delete()

    return Response({'success': 'Friend request cancelled successfully'}, status=status.HTTP_200_OK)


class RemoveFriendView(APIView):
  permission_classes = [permissions.IsAuthenticated]

  def post(self, request):
    data = request.data
    friend_id = data.get('friend_id')

    if not friend_id:
      return Response({'error': 'friend_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    if not request.user.friends.filter(id=friend_id).exists():
      return Response({'error': 'You are not friends with this user'}, status=status.HTTP_400_BAD_REQUEST)

    friend = User.objects.get(id=friend_id)

    request.user.friends.remove(friend)
    friend.friends.remove(request.user)

    return Response({'success': 'Friend removed successfully'}, status=status.HTTP_200_OK)


class GetFriendsView(APIView):
  permission_classes = [permissions.IsAuthenticated]

  def get(self, request):
    friends = request.user.friends.all()
    friends = UserSerializer(friends, many=True)

    return Response(friends.data, status=status.HTTP_200_OK)


class GetFriendRequestsSentView(APIView):
  permission_classes = [permissions.IsAuthenticated]

  def get(self, request):
    friend_requests = request.user.friend_requests_sent.all()
    friend_requests = FriendRequestSerializer(friend_requests, many=True)

    return Response(friend_requests.data, status=status.HTTP_200_OK)


class GetFriendRequestsReceivedView(APIView):
  permission_classes = [permissions.IsAuthenticated]

  def get(self, request):
    friend_requests = request.user.friend_requests_received.all()
    friend_requests = FriendRequestSerializer(friend_requests, many=True)

    return Response(friend_requests.data, status=status.HTTP_200_OK)
