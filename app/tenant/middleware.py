from typing import Type
from django.db import connection
from django.http.request import HttpRequest

from django_tenants.utils import get_tenant_model
from django_tenants.middleware import TenantMainMiddleware

from tenant.models import Tenant


class XTenantMiddleware(TenantMainMiddleware):
    def process_request(self, request: HttpRequest):
        connection.set_schema_to_public()
        hostname: str = self.hostname_from_request(request)
        tenant_model: Tenant = get_tenant_model()

        try:
            tenant = self.get_tenant(tenant_model, request)
        except tenant_model.DoesNotExist:
            self.no_tenant_found(request, hostname)

        tenant.domain_url = hostname
        request.tenant = tenant
        connection.set_tenant(request.tenant)
        self.setup_url_routing(request)

    def get_tenant(
        self, tenant_model: Type[Tenant], request: HttpRequest
    ) -> Type[Tenant]:
        if domain := request.headers.get("X-Tenant"):
            return tenant_model.objects.get(domains__domain=domain)
        else:
            return tenant_model.objects.get(
                domains__domain=self.hostname_from_request(request)
            )
