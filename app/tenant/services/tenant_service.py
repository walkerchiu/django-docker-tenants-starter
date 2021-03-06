from typing import Tuple
import uuid

from django.conf import settings
from django.db import transaction
from django.db.utils import IntegrityError

from safedelete.models import HARD_DELETE

from tenant.models import Contract, Domain, Tenant


class TenantService:
    @transaction.atomic
    def create_tenant(self, subdomain: str, email: str) -> Tuple[bool, Tenant]:
        schema_name = str(uuid.uuid4()).replace("-", "")

        tenant = Tenant(
            schema_name=schema_name,
            email=email,
        )
        tenant.save()

        try:
            # Add contract for the tenant
            contract = Contract(
                tenant=tenant,
            )
            contract.save()

            # Add a domain for the tenant
            domain = Domain(
                tenant=tenant,
                domain=subdomain + "." + settings.APP_DOMAIN,
                is_primary=True,
                is_builtin=True,
            )
            domain.save()

        except IntegrityError:
            result = False
        else:
            result = True

        if not result:
            tenant.delete(force_policy=HARD_DELETE)
            tenant = False

        return result, tenant

    @transaction.atomic
    def delete_tenant(self, tenant_id: uuid) -> bool:
        try:
            tenant = Tenant.objects.get(pk=tenant_id)
        except Tenant.DoesNotExist:
            return False

        tenant.delete()

        return True

    @transaction.atomic
    def undelete_tenant(self, tenant_id: uuid) -> bool:
        try:
            tenant = Tenant.deleted_objects.get(pk=tenant_id)
        except Tenant.DoesNotExist:
            return False

        tenant.undelete()

        return True
