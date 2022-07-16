from typing import Tuple
import uuid

from django.db import transaction
from django.db.utils import ProgrammingError

from django_tenants.utils import schema_context
from safedelete.models import HARD_DELETE

from account.models import User
from account.services.user_service import UserService
from organization.models import Organization, OrganizationTrans


class OrganizationService:
    @transaction.atomic
    def initiate_schema(
        self, schema_name: str, organization_name: str, email: str, password: str
    ) -> Tuple[bool, Organization, User]:
        with schema_context(schema_name):
            try:
                organization = Organization(
                    schema_name=schema_name,
                )
                organization.save()
                OrganizationTrans.objects.create(
                    organization=organization,
                    language_code=organization.language_code,
                    name=organization_name,
                )

                user_service = UserService()
                result, user = user_service.create_user(
                    schema_name=schema_name,
                    email=email,
                    password=password,
                    name="demo",
                )

                if result:
                    return True, organization, user
                else:
                    organization.delete(force_policy=HARD_DELETE)
                    return False, None, None
            except ProgrammingError:
                return False, None, None

    @transaction.atomic
    def delete_organization(self, schema_name: str, organization_id: uuid) -> bool:
        with schema_context(schema_name):
            try:
                organization = Organization.objects.get(pk=organization_id)
            except ProgrammingError:
                return False
            except Organization.DoesNotExist:
                return False

            organization.delete()

        return True

    @transaction.atomic
    def undelete_organization(self, schema_name: str, organization_id: uuid) -> bool:
        with schema_context(schema_name):
            try:
                organization = Organization.deleted_objects.get(pk=organization_id)
            except ProgrammingError:
                return False
            except Organization.DoesNotExist:
                return False

            organization.undelete()

        return True
