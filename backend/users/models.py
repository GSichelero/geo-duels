from django.db import models
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
