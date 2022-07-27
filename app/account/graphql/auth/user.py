from datetime import datetime, timedelta
import re
import secrets
import string

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import connection, transaction
from django.db.models import Q

from django_tenants.utils import schema_context
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required
import graphene

from account.models import PasswordReset, User
from core.relay.connection import ExtendedConnection
from account.services.user_service import UserService
from tenant.models import Domain, Tenant
from tenant.services.tenant_service import TenantService


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id", "email", "name", "profile")


class UserConnection(graphene.relay.Connection):
    class Meta:
        node = UserType


class TenantsType(graphene.ObjectType):
    domain = graphene.String()


class UserNode(DjangoObjectType):
    class Meta:
        model = User
        filter_fields = {
            "id": ["exact"],
            "email": ["iexact", "icontains", "istartswith"],
            "name": ["iexact", "icontains", "istartswith"],
        }
        fields = ("id", "profile", "email", "name")
        order_by_field = "email"
        interfaces = (graphene.relay.Node,)
        connection_class = ExtendedConnection

    tenants = graphene.List(TenantsType)

    @classmethod
    def get_queryset(cls, queryset, info):
        if info.context.user.is_anonymous or (
            not info.context.user.is_hq_user and not info.context.user.is_staff
        ):
            raise Exception("Bad Request!")
        return queryset

    @classmethod
    def get_node(cls, info, id):
        if info.context.user.is_anonymous:
            raise Exception("Bad Request!")

        try:
            user = cls._meta.model.objects.get(pk=id)
        except cls._meta.model.DoesNotExist:
            raise Exception("Bad Request!")

        if (
            info.context.user.is_hq_user
            or info.context.user.is_admin
            or info.context.user.id == user.id
        ):
            return user

        raise Exception("Bad Request!")

    def resolve_tenants(parent, info):
        with schema_context(settings.PUBLIC_SCHEMA_NAME):
            tenants = []
            email = info.context.user.email
            records = Tenant.objects.filter(email=email)
            for record in records:
                domain = Domain.objects.get(tenant=record, is_builtin=True)
                tenants.append({"domain": domain.domain})
        return tenants


class RegisterCustomer(graphene.relay.ClientIDMutation):
    class Input:
        email = graphene.String(required=True)
        password = graphene.String()

    success = graphene.Boolean()

    @classmethod
    @login_required
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info, **input):
        email = input["email"]
        password = input["password"]

        if not re.fullmatch(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", email
        ):
            raise ValidationError("The email is invalid!")

        user_service = UserService()
        result, user = user_service.register_customer(
            schema_name=connection.schema_name,
            email=email,
            password=password,
        )

        if result:
            return RegisterCustomer(success=True)
        else:
            raise Exception("Can not register this customer!")


class UpdateUser(graphene.relay.ClientIDMutation):
    class Input:
        email = graphene.String(required=True)
        name = graphene.String(required=True)

    success = graphene.Boolean()

    @classmethod
    @login_required
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info, **input):
        email = input["email"]
        name = input["name"]

        if not re.fullmatch(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", email
        ):
            raise ValidationError("The email is invalid!")

        user = info.context.user
        email_original = user.email

        user.email = email
        user.name = name
        user.save()

        if info.context.user.is_owner and email_original != user.email:
            with schema_context(settings.PUBLIC_SCHEMA_NAME):
                tenant_service = TenantService()
                tenant_service.updateEmail(
                    email_original=email_original, email_new=user.email
                )

        return UpdateUser(success=True)


class ForgotPassword(graphene.relay.ClientIDMutation):
    class Input:
        email = graphene.String(required=True)

    success = graphene.Boolean()

    @classmethod
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info, **input):
        email = input["email"]

        if not re.fullmatch(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", email
        ):
            raise ValidationError("The email is invalid!")

        try:
            user = User.objects.get(email=email)

            range_start = datetime.now() - timedelta(minutes=10)
            PasswordReset.objects.filter(
                Q(user=user) | Q(created_at__lt=range_start)
            ).delete()

            alphabet = string.ascii_letters + string.digits
            token = "".join(secrets.choice(alphabet) for i in range(100))
            PasswordReset.objects.create(user=user, token=token)

            auth_helper = AuthHelper()
            auth_helper.send_email_with_token(
                type="forgot-password", email=user.email, token=token
            )
        except User.DoesNotExist:
            raise Exception("Can not find this user!")

        return ForgotPassword(success=True)


class ResetPassword(graphene.relay.ClientIDMutation):
    class Input:
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        resetToken = graphene.String(required=True)

    success = graphene.Boolean()

    @classmethod
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info, **input):
        email = input["email"]
        password = input["password"]
        resetToken = input["resetToken"]

        if not re.fullmatch(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", email
        ):
            raise ValidationError("The email is invalid!")
        elif len(resetToken) != 100:
            raise ValidationError("The reset_token is invalid!")

        try:
            user = User.objects.get(email=email)

            range_start = datetime.now() - timedelta(minutes=10)
            record = PasswordReset.objects.filter(
                user=user, token=resetToken, created_at__gte=range_start
            ).first()
            if record:
                user.set_password(password)
                user.save()

                record.delete()

                auth_helper = AuthHelper()
                auth_helper.send_email(type="reset-password", email=user.email)
            else:
                raise ValidationError("The reset_token is invalid!")
        except User.DoesNotExist:
            raise Exception("Can not find this user!")

        return ResetPassword(success=True)


class UserQuery(graphene.ObjectType):
    pass


class UserMutation(graphene.ObjectType):
    register_customer = RegisterCustomer.Field()
    update_user = UpdateUser.Field()
    forgot_password = ForgotPassword.Field()
    reset_password = ResetPassword.Field()
