import uuid

from django.conf import settings
from django.db import models

from django_tenants.models import TenantMixin, DomainMixin
from safedelete.models import SOFT_DELETE_CASCADE

from core.models import CreateUpdateDateAndSafeDeleteMixin, PublishableModel


class Tenant(TenantMixin, CreateUpdateDateAndSafeDeleteMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    schema_name = models.CharField(max_length=32)
    email = models.EmailField(
        verbose_name="email address", max_length=255, db_index=True
    )

    _safedelete_policy = SOFT_DELETE_CASCADE
    auto_create_schema = True
    auto_drop_schema = True

    class Meta:
        db_table = settings.APP_NAME + "_tenant_tenant"
        ordering = ["id"]

    def __str__(self):
        return str(self.id)


class Contract(CreateUpdateDateAndSafeDeleteMixin, PublishableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, models.CASCADE)
    slug = models.CharField(max_length=32, unique=True, db_index=True)
    type = models.CharField(max_length=10, null=True)
    note = models.CharField(max_length=255, blank=True, null=True)
    expired_on = models.DateField(null=True)

    _safedelete_policy = SOFT_DELETE_CASCADE

    class Meta:
        db_table = settings.APP_NAME + "_tenant_contract"
        ordering = ["slug"]

    def __str__(self):
        return self.slug


class Domain(DomainMixin, CreateUpdateDateAndSafeDeleteMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        settings.TENANT_MODEL,
        db_index=True,
        related_name="domains",
        on_delete=models.CASCADE,
    )
    domain = models.CharField(max_length=253, unique=True, db_index=True)
    is_builtin = models.BooleanField(default=False)

    _safedelete_policy = SOFT_DELETE_CASCADE

    class Meta:
        db_table = settings.APP_NAME + "_tenant_domain"
        ordering = ["domain"]

    def __str__(self):
        return str(self.id)
