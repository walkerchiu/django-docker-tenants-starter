import datetime

from django.db import models
from django.db.models import Q

from safedelete.models import SafeDeleteModel


class CreateUpdateDateAndSafeDeleteMixin(SafeDeleteModel):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class PublishedQuerySet(models.QuerySet):
    def published(self):
        today = datetime.date.today()
        return self.filter(
            Q(published_at__lte=today) | Q(published_at__isnull=True),
            is_published=True,
        )


class PublishableModel(models.Model):
    is_published = models.BooleanField(default=False)
    published_at = models.DateField(null=True)

    objects = models.Manager.from_queryset(PublishedQuerySet)()

    class Meta:
        abstract = True

    @property
    def is_visible(self) -> bool:
        return self.is_published and (
            self.published_at is None or self.published_at <= datetime.date.today()
        )


class TranslationModel(models.Model):
    language_code = models.CharField(max_length=35, default="zh-TW")

    class Meta:
        abstract = True
