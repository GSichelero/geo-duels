from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from .models import FriendInvited, FriendRequest, Room, RoomConfig, RoomMember, GeoPoint, Guessings, Round
from rest_framework import serializers
from django.contrib.auth import get_user_model
User = get_user_model()


class UserCreateSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ('first_name', 'last_name', 'email', 'nickname', 'password')

  def validate(self, data):
    user = User(**data)
    password = data.get('password')

    try:
      validate_password(password, user)
    except exceptions.ValidationError as e:
      serializer_errors = serializers.as_serializer_error(e)
      raise exceptions.ValidationError(
        {'password': serializer_errors['non_field_errors']}
      )

    return data


  def create(self, validated_data):
    user = User.objects.create_user(
      first_name=validated_data['first_name'],
      last_name=validated_data['last_name'],
      nickname=validated_data['nickname'],
      email=validated_data['email'],
      password=validated_data['password'],
    )

    return user


class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ('id', 'first_name', 'last_name', 'nickname', 'email', 'friends')


class FriendRequestSerializer(serializers.ModelSerializer):
  # return the user object instead of the user id
  from_user = UserSerializer(read_only=True)
  to_user = UserSerializer(read_only=True)

  class Meta:
    model = FriendRequest
    fields = ('id', 'from_user', 'to_user')


# class Guessings(mongo_models.Model):
#   id = mongo_models.ObjectIdField(default=1)
#   guess_number = mongo_models.IntegerField()
#   guess_geopoint = mongo_models.EmbeddedField(
#     model_container=GeoPoint,
#     model_form_class=GeoPoint,
#   )

# class Round(mongo_models.Model):
#   id = mongo_models.ObjectIdField(default=1)
#   round_number = mongo_models.IntegerField()
#   guessings = mongo_models.ArrayField(
#     model_container=Guessings,
#     model_form_class=Guessings,
#   )
#   picking = mongo_models.EmbeddedField(
#     model_container=GeoPoint,
#     model_form_class=GeoPoint,
#   )

# class RoomMember(mongo_models.Model):
#   id = mongo_models.ObjectIdField(default=1)
#   user_number = mongo_models.IntegerField()
#   username = mongo_models.CharField(max_length=15, blank=False, null=False, unique=True, validators=[MinLengthValidator(3)])
#   score = mongo_models.IntegerField(default=0)
#   is_ready = mongo_models.BooleanField(default=False)
#   rounds = mongo_models.ArrayField(
#     model_container=Round,
#     model_form_class=Round,
#   )

# class RoomConfig(mongo_models.Model):
#   id = mongo_models.ObjectIdField(default=1)
#   max_members = mongo_models.IntegerField(default=4)
#   number_of_rounds = mongo_models.IntegerField(default=3)
#   time_per_pick = mongo_models.IntegerField(default=30)
#   time_per_guess = mongo_models.IntegerField(default=30)
#   moving_allowed = mongo_models.BooleanField(default=True)

# class FriendInvited(mongo_models.Model):
#   id = mongo_models.ObjectIdField(default=1)
#   username = mongo_models.CharField(max_length=15)


# class Room(mongo_models.Model):
#   _id = mongo_models.ObjectIdField()
#   room_name = mongo_models.TextField(max_length=30)
#   room_password = mongo_models.TextField(max_length=30)
#   room_owner = mongo_models.TextField(max_length=15)
#   room_state = mongo_models.TextField(max_length=30)
#   room_round = mongo_models.IntegerField(default=0)
#   is_active = mongo_models.BooleanField(default=True)
#   invited_users = mongo_models.ArrayField(
#     model_container=FriendInvited,
#     model_form_class=FriendInvited,
#   )
#   room_members = mongo_models.ArrayField(
#     model_container=RoomMember,
#     model_form_class=RoomMember,
#   )
#   room_configs = mongo_models.EmbeddedField(
#     model_container=RoomConfig,
#     model_form_class=RoomConfig,
#   )
# serialize the above classes as a json object


class GeoPointSerializer(serializers.ModelSerializer):
  class Meta:
    model = GeoPoint
    fields = ('lat', 'lng')

class GuessingsSerializer(serializers.ModelSerializer):
  guess_geopoint = GeoPointSerializer(read_only=True, many=False)

  class Meta:
    model = Guessings
    fields = ('guess_number', 'guess_geopoint')

class RoundSerializer(serializers.ModelSerializer):
  guessings = GuessingsSerializer(read_only=True, many=True)
  picking = GeoPointSerializer(read_only=True, many=False)

  class Meta:
    model = Round
    fields = ('round_number', 'guessings', 'picking')
    
class RoomMemberSerializer(serializers.ModelSerializer):
  rounds = RoundSerializer(required=False, read_only=True, many=True)

  class Meta:
    model = RoomMember
    fields = ('user_number', 'username', 'score', 'is_ready', 'rounds')

class FriendInvitedSerializer(serializers.ModelSerializer):
  class Meta:
    model = FriendInvited
    fields = ('username')

class RoomConfigSerializer(serializers.ModelSerializer):
  class Meta:
    model = RoomConfig
    fields = ('max_members', 'number_of_rounds', 'time_per_pick', 'time_per_guess', 'moving_allowed')

class RoomSerializer(serializers.ModelSerializer):
  room_members = RoomMemberSerializer(required=False, read_only=True, many=True)
  invited_users = FriendInvitedSerializer(required=False, read_only=True, many=True)
  room_configs = RoomConfigSerializer(required=False, read_only=True, many=False)

  class Meta:
    model = Room
    fields = ['_id', 'room_name', 'room_password', 'room_owner', 'room_state', 'room_round', 'is_active', 'invited_users', 'room_members', 'room_configs']
