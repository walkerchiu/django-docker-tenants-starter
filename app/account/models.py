import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

from safedelete.models import SafeDeleteModel, SOFT_DELETE_CASCADE

from core.models import CreateUpdateDateAndSafeDeleteMixin


class UserManager(BaseUserManager):
    pass


class User(CreateUpdateDateAndSafeDeleteMixin, AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(
        verbose_name="email address", max_length=255, unique=True, db_index=True
    )
    name = models.CharField(max_length=255, db_index=True)
    email_verified = models.BooleanField(default=False)

    objects = UserManager()

    _safedelete_policy = SOFT_DELETE_CASCADE

    USERNAME_FIELD = "email"

    class Meta:
        db_table = settings.APP_NAME + "_account_user"
        ordering = ["email"]

    def __str__(self):
        return str(self.id)


class Profile(SafeDeleteModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, models.CASCADE)
    birth = models.DateField(null=True)

    _safedelete_policy = SOFT_DELETE_CASCADE

    class Meta:
        db_table = settings.APP_NAME + "_account_profile"


class PasswordReset(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, models.CASCADE)
    token = models.CharField(max_length=255, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = settings.APP_NAME + "_account_password_reset"
        index_together = (("user", "token", "created_at"),)
        ordering = ["id"]

    def __str__(self):
        return str(self.id)
