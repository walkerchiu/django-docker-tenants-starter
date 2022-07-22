from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import connection

from django_tenants.utils import schema_context
from graphene.utils.thenables import maybe_thenable
from graphql_jwt.decorators import token_auth
from graphql_jwt.refresh_token.mutations import DeleteRefreshTokenCookie, Revoke
import graphene

from core.graphql_jwt import mixins
from tenant.models import Tenant

__all__ = [
    "JSONWebTokenMutation",
    "ObtainJSONWebToken",
    "Verify",
    "Refresh",
    "Revoke",
    "DeleteRefreshTokenCookie",
]


class JSONWebTokenMutation(mixins.ObtainJSONWebTokenMixin, graphene.ClientIDMutation):
    class Meta:
        abstract = True

    @classmethod
    def Field(cls, *args, **kwargs):
        cls._meta.arguments["input"]._meta.fields.update(
            {
                get_user_model().USERNAME_FIELD: graphene.InputField(
                    graphene.String,
                    required=True,
                ),
                "password": graphene.InputField(graphene.String, required=True),
            },
        )
        return super().Field(*args, **kwargs)

    @classmethod
    def mutate(cls, root, info, input):
        def on_resolve(payload):
            try:
                payload.client_mutation_id = input.get("client_mutation_id")
            except Exception:
                raise Exception(
                    f"Cannot set client_mutation_id in the payload object {repr(payload)}"
                )
            return payload

        schema_name = connection.schema_name

        if (
            info.context.headers.get("X-Tenant")
            == "account" + "." + settings.APP_DOMAIN
        ):
            with schema_context(settings.PUBLIC_SCHEMA_NAME):
                tenant = (
                    Tenant.objects.filter(email=input.get("email"))
                    .order_by("created_at")
                    .first()
                )
                if tenant:
                    schema_name = tenant.schema_name
                else:
                    raise Exception("Please enter valid credentials")

        with schema_context(schema_name):
            result = cls.mutate_and_get_payload(root, info, **input)
            return maybe_thenable(result, on_resolve)

    @classmethod
    @token_auth
    def mutate_and_get_payload(cls, root, info, **kwargs):
        return cls.resolve(root, info, **kwargs)


class ObtainJSONWebToken(mixins.ResolveMixin, JSONWebTokenMutation):
    """Obtain JSON Web Token mutation"""


class Verify(mixins.VerifyMixin, graphene.ClientIDMutation):
    class Input:
        token = graphene.String()

    @classmethod
    def mutate_and_get_payload(cls, *args, **kwargs):
        return cls.verify(*args, **kwargs)


class Refresh(mixins.RefreshMixin, graphene.ClientIDMutation):
    class Input(mixins.RefreshMixin.Fields):
        """Refresh Input"""

    @classmethod
    def mutate_and_get_payload(cls, *args, **kwargs):
        return cls.refresh(*args, **kwargs)


class DeleteJSONWebTokenCookie(
    mixins.DeleteJSONWebTokenCookieMixin,
    graphene.ClientIDMutation,
):
    @classmethod
    def mutate_and_get_payload(cls, *args, **kwargs):
        return cls.delete_cookie(*args, **kwargs)
