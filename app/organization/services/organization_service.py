from typing import Tuple
import uuid

from django_tenants.utils import schema_context

from organization.models import Organization


class OrganizationService:
    def initiate_schema(
        self, schema_name: str, organization_name: str, email: str, password: str
    ) -> Tuple[bool, Organization]:
        with schema_context(schema_name):
            result, organization = self.create_organization(
                schema_name=schema_name,
                organization_name=organization_name,
            )

        return result, organization

    def create_organization(
        self, schema_name: str, organization_name: str
    ) -> Tuple[bool, Organization]:
        with schema_context(schema_name):
            organization = Organization(
                schema_name=schema_name,
                name=organization_name,
            )
            organization.save()

        return True, organization

    def delete_organization(self, schema_name: str, organization_id: uuid) -> bool:
        with schema_context(schema_name):
            try:
                organization = Organization.objects.get(pk=organization_id)
            except Organization.DoesNotExist:
                return False

            organization.delete()

        return True

    def undelete_organization(self, schema_name: str, organization_id: uuid) -> bool:
        with schema_context(schema_name):
            try:
                organization = Organization.deleted_objects.get(pk=organization_id)
            except Organization.DoesNotExist:
                return False

            organization.undelete()

        return True
