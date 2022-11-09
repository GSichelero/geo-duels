from .models import FriendRequest, Room, RoomMember, RoomConfig, Round, Guessings
from bson.objectid import ObjectId
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from .serializers import FriendRequestSerializer, User, UserCreateSerializer, UserSerializer, RoomSerializer


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


class GetAllUsersView(APIView):
  permission_classes = [permissions.IsAuthenticated]

  def get(self, request):
    users = User.objects.all()
    users = UserSerializer(users, many=True)

    return Response(users.data, status=status.HTTP_200_OK)


class CreateRoomView(APIView):
  permission_classes = [permissions.IsAuthenticated]

  def post(self, request):
    if not Room.objects.using('nonrel').filter(room_name=request.data['room_name']).exists():
      room = Room(
          room_name=request.data['room_name'],
          room_password=request.data['room_password'],
          room_owner=request.user.nickname,
          room_state='waiting',
          room_round=0,
          player_turn=0,
          room_deadline_time=0,
          is_active=True,
          room_members=[],
          invited_users=[],
          room_configs={
              'id': 1,
              'max_members': request.data['max_members'],
              'number_of_rounds': request.data['number_of_rounds'],
              'time_per_pick': request.data['time_per_pick'],
              'time_per_guess': request.data['time_per_guess'],
              'moving_allowed': request.data['moving_allowed'] == 'true',
          }   
      )
      room.save(using='nonrel')
      return Response({
        'roomId': str(room._id),
        'roomName': room.room_name,
        'roomPassword': room.room_password,
        'roomOwner': room.room_owner,
        'isActive': room.is_active,
        'roomMembers': room.room_members,
        'max_members': room.room_configs.get('max_members'),
        }, status=status.HTTP_200_OK)

    else:
      return Response({'error': 'Room name already exists'}, status=status.HTTP_400_BAD_REQUEST)


class InviteFriendView(APIView):
  permission_classes = [permissions.IsAuthenticated]

  def post(self, request):
    # receive room id and friend username
    room_id = ObjectId(request.data['room_id'])
    friend_username = request.data['friend_username']

    # add the friend username to the invited_users array
    room = Room.objects.using('nonrel').get(_id=room_id)
    # if username not already in invited_users.username
    if friend_username not in [member['username'] for member in room.invited_users]:
      room.invited_users.append({'id': 1, 'username': friend_username})
      room.save(using='nonrel')

    return Response({'success': 'Friend invited'}, status=status.HTTP_200_OK)


class GetReceivedInvites(APIView):
  permission_classes = [permissions.IsAuthenticated]

  def get(self, request):
    # get all rooms where the user nickname is in the list of users invited and the room is active
    rooms = Room.objects.using('nonrel').filter(invited_users={'username':request.user.nickname}).all()

    # return a list of rooms with the room id, room name, room password, room owner, and room configs
    return Response([{
        'roomId': str(room._id),
        'roomName': room.room_name,
        'roomPassword': room.room_password,
        'roomOwner': room.room_owner,
        'roomConfigs': room.room_configs,
      } for room in rooms], status=status.HTTP_200_OK)


class RejectInviteView(APIView):
  permission_classes = [permissions.IsAuthenticated]

  def post(self, request):
    # receive room id
    room_id = ObjectId(request.data['room_id'])

    # get the room
    room = Room.objects.using('nonrel').get(_id=room_id)

    # remove the user from the invited users list
    room.invited_users = [user for user in room.invited_users if user['username'] != request.user.nickname]
    room.save(using='nonrel')

    return Response({'success': 'Invite rejected'}, status=status.HTTP_200_OK)


class JoinRoomView(APIView):
  permission_classes = [permissions.IsAuthenticated]
  
  def post(self, request):
    # receive room id
    room_name = request.data['room_name']
    room_password = request.data['room_password']

    # get the room with name and password
    room = Room.objects.using('nonrel').get(room_name=room_name, room_password=room_password)
    
    # if user.nickname not already in the username field inside the list of room_member, add the user to the room members list
    if len(room.room_members) < room.room_configs.get('max_members') and request.user.nickname not in [member['username'] for member in room.room_members]:
      room.room_members.append({
        'id': 1,
        'user_number': len(room.room_members) + 1,
        'username': request.user.nickname,
        'score': 0,
        'is_ready': False,
        'rounds': [],
      })

      # save the room
      room.save(using='nonrel')

      return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)

    elif request.user.nickname in [member['username'] for member in room.room_members]:
      return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)

    else:
      return Response({'error': 'Room is full'}, status=status.HTTP_400_BAD_REQUEST)
