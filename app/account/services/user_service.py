from typing import Tuple
import uuid

from django.db.utils import ProgrammingError

from django_tenants.utils import schema_context

from account.models import Profile, User


class UserService:
    def create_user(
        self, schema_name: str, email: str, password: str, name: str = ""
    ) -> Tuple[bool, User]:
        with schema_context(schema_name):
            try:
                user = User(
                    email=email,
                    name=name,
                )
                user.set_password(password)
                user.save()

                Profile.objects.create(user=user)
            except ProgrammingError:
                return False, None

        return True, user

    def undelete_user(self, schema_name: str, id: uuid) -> bool:
        with schema_context(schema_name):
            try:
                user = User.deleted_objects.get(pk=id)
            except ProgrammingError:
                return False
            except User.DoesNotExist:
                return False
            else:
                user.undelete()

        return True
