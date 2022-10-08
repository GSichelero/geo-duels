from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from .models import FriendRequest
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
