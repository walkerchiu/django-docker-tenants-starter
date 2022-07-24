from graphql.backend.core import GraphQLCoreBackend


def measure_depth(selection_set, level=1):
    max_depth = level
    for field in selection_set.selections:
        if field.selection_set:
            new_depth = measure_depth(field.selection_set, level=level + 1)
            if new_depth > max_depth:
                max_depth = new_depth
    return max_depth


class DepthAnalysisBackend(GraphQLCoreBackend):
    def document_from_string(self, schema, document_string):
        document = super().document_from_string(schema, document_string)
        ast = document.document_ast
        for definition in ast.definitions:
            if len(definition.selection_set.selections) > 1:
                raise Exception("Query is too complex")

            depth = measure_depth(definition.selection_set)
            if depth > 12:  # set your depth max here
                raise Exception("Query is too nested")

        return document
