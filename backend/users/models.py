from django.db import models
from djongo import models as mongo_models
from django.core.validators import MinLengthValidator
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin


class UserAccountManager(BaseUserManager):
  def create_user(self, first_name, last_name, nickname, email, password=None):
    if not email:
      raise ValueError('Users must have an email address')
    if not nickname:
      raise ValueError('Users must have a nickname')

    email = self.normalize_email(email)
    email = email.lower()

    user = self.model(
      first_name=first_name,
      last_name=last_name,
      email=email,
      nickname=nickname,
    )

    user.set_password(password)
    user.save(using=self._db)

    return user
  
  def create_superuser(self, first_name, last_name, nickname, email, password=None):
    user = self.create_user(
      first_name,
      last_name,
      nickname,
      email,
      password=password,
    )

    user.is_staff = True
    user.is_superuser = True
    user.save(using=self._db)

    return user


class UserAccount(AbstractBaseUser, PermissionsMixin):
  first_name = models.CharField(max_length=255)
  last_name = models.CharField(max_length=255)
  nickname = models.CharField(max_length=15, blank=False, null=False, unique=True, validators=[MinLengthValidator(3)])
  email = models.EmailField(unique=True, max_length=255)
  is_active = models.BooleanField(default=True)
  is_staff = models.BooleanField(default=False)
  friends = models.ManyToManyField('self', blank=True)

  objects = UserAccountManager()

  USERNAME_FIELD = 'email'
  REQUIRED_FIELDS = ['first_name', 'last_name', 'nickname']

  def __str__(self):
    return self.email


class FriendRequest(models.Model):
  from_user = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='friend_requests_sent')
  to_user = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='friend_requests_received')
  timestamp = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return f'{self.from_user} to {self.to_user}'

  class Meta:
    unique_together = ('from_user', 'to_user')
    ordering = ('-timestamp',)


class GeoPoint(mongo_models.Model):
  id = mongo_models.ObjectIdField(default=1)
  lat = mongo_models.FloatField()
  lng = mongo_models.FloatField()

  class Meta:
    abstract = True

  def __str__(self):
    return f'({self.lat}, {self.lng})'

class Guessings(mongo_models.Model):
  id = mongo_models.ObjectIdField(default=1)
  guess_number = mongo_models.IntegerField()
  guess_geopoint = mongo_models.EmbeddedField(
    model_container=GeoPoint,
    model_form_class=GeoPoint,
  )

class Round(mongo_models.Model):
  id = mongo_models.ObjectIdField(default=1)
  round_number = mongo_models.IntegerField()
  guessings = mongo_models.ArrayField(
    model_container=Guessings,
    model_form_class=Guessings,
  )
  picking = mongo_models.EmbeddedField(
    model_container=GeoPoint,
    model_form_class=GeoPoint,
  )

class RoomMember(mongo_models.Model):
  id = mongo_models.ObjectIdField(default=1)
  user_number = mongo_models.IntegerField()
  username = mongo_models.CharField(max_length=15, blank=False, null=False, unique=True, validators=[MinLengthValidator(3)])
  score = mongo_models.IntegerField(default=0)
  is_ready = mongo_models.BooleanField(default=False)
  rounds = mongo_models.ArrayField(
    model_container=Round,
    model_form_class=Round,
  )

class RoomConfig(mongo_models.Model):
  id = mongo_models.ObjectIdField(default=1)
  max_members = mongo_models.IntegerField(default=4)
  number_of_rounds = mongo_models.IntegerField(default=3)
  time_per_pick = mongo_models.IntegerField(default=30)
  time_per_guess = mongo_models.IntegerField(default=30)
  moving_allowed = mongo_models.BooleanField(default=True)

class FriendInvited(mongo_models.Model):
  id = mongo_models.ObjectIdField(default=1)
  username = mongo_models.CharField(max_length=15)


class Room(mongo_models.Model):
  _id = mongo_models.ObjectIdField()
  room_name = mongo_models.TextField(max_length=30)
  room_password = mongo_models.TextField(max_length=30)
  room_owner = mongo_models.TextField(max_length=15)
  room_state = mongo_models.TextField(max_length=30)
  room_round = mongo_models.IntegerField(default=0)
  is_active = mongo_models.BooleanField(default=True)
  invited_users = mongo_models.ArrayField(
    model_container=FriendInvited,
    model_form_class=FriendInvited,
  )
  room_members = mongo_models.ArrayField(
    model_container=RoomMember,
    model_form_class=RoomMember,
  )
  room_configs = mongo_models.EmbeddedField(
    model_container=RoomConfig,
    model_form_class=RoomConfig,
  )

  def __str__(self):
    return self.room_name

  class Meta:
    _use_db = 'nonrel'
