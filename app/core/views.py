import re

from graphene_django.views import GraphQLView


class ErrorGraphQLView(GraphQLView):
    def execute_graphql_request(self, *args, **kwargs):
        result = super().execute_graphql_request(*args, **kwargs)
        if result.errors:
            for error in result.errors:
                try:
                    raise error.original_error
                except Exception as e:
                    for arg in e.args:
                        try:
                            if "IntegrityError" in arg and "is not present" in str(
                                error
                            ):
                                string = re.search("Key \\((.*)\\)=", str(error)).group(
                                    1
                                )
                                if string:
                                    string = re.search("(.*)_", string).group(1)
                                result.errors = ["Can not find this " + string + "!"]
                        except TypeError:
                            pass
        return result
