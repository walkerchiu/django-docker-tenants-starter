from django.utils import timezone

from graphql_jwt.settings import jwt_settings
from graphql_relay import to_global_id


def jwt_payload(user, context=None):
    jwt_datetime = timezone.now() + jwt_settings.JWT_EXPIRATION_DELTA
    jwt_expires = int(jwt_datetime.timestamp())

    user.last_login = timezone.now()
    user.save()

    payload = {}
    payload["email"] = str(user.email)
    payload["sub"] = to_global_id("User", user.id)
    payload["exp"] = jwt_expires

    return payload
