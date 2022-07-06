import uuid

from django.conf import settings
from django.db import models

from safedelete.models import SOFT_DELETE_CASCADE

from core.models import CreateUpdateDateAndSafeDeleteMixin, PublishableModel


class Organization(CreateUpdateDateAndSafeDeleteMixin, PublishableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    schema_name = models.CharField(max_length=32, db_index=True)
    name = models.CharField(max_length=255, db_index=True)

    _safedelete_policy = SOFT_DELETE_CASCADE

    class Meta:
        db_table = settings.APP_NAME + "_organization_organization"
        ordering = ["name"]

    def __str__(self):
        return str(self.id)
