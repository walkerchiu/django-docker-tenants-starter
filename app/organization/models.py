import uuid

from django.conf import settings
from django.db import models

from safedelete.models import SOFT_DELETE_CASCADE

from core.models import CreateUpdateDateAndSafeDeleteMixin, PublishableModel, TranslationModel


class Organization(CreateUpdateDateAndSafeDeleteMixin, PublishableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    schema_name = models.CharField(max_length=32, db_index=True)
    language_code = models.CharField(max_length=35, default="zh-TW")

    _safedelete_policy = SOFT_DELETE_CASCADE

    class Meta:
        db_table = settings.APP_NAME + "_organization_organization"
        ordering = ["language_code"]

    def __str__(self):
        return str(self.id)


class OrganizationTrans(CreateUpdateDateAndSafeDeleteMixin, TranslationModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization, related_name="translations", on_delete=models.CASCADE, null=True
    )
    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True, null=True)

    _safedelete_policy = SOFT_DELETE_CASCADE

    class Meta:
        db_table = settings.APP_NAME + "_organization_organization_trans"
        index_together = (("language_code", "organization"),)
        ordering = ["language_code"]

    def __str__(self):
        return str(self.id)
