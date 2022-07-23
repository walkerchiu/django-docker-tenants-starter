import graphene

from account.graphql.schema_auth import UserMutation
from core.graphql_jwt.mutations import ObtainJSONWebToken, Verify


class Query(
    graphene.ObjectType,
):
    pass


class Mutation(
    UserMutation,
    graphene.ObjectType,
):
    token_auth = ObtainJSONWebToken.Field()
    verify_token = Verify.Field()


schema = graphene.Schema(mutation=Mutation)
