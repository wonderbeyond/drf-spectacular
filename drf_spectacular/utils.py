import inspect

from rest_framework.settings import api_settings

from drf_spectacular.types import resolve_basic_type


class PolymorphicResponse:
    def __init__(self, serializers, resource_type_field_name):
        self.serializers = serializers
        self.resource_type_field_name = resource_type_field_name


class OpenApiSchemaBase:
    """ reusable base class for objects that can be translated to a schema """

    def to_schema(self):
        raise NotImplementedError('translation to schema required.')


class QueryParameter(OpenApiSchemaBase):
    def __init__(self, name, description='', required=False, type=str):
        self.name = name
        self.description = description
        self.required = required
        self.type = type

    def to_schema(self):
        return {
            'name': self.name,
            'in': 'query',
            'description': self.description,
            'required': self.required,
            'schema': resolve_basic_type(self.type)
        }


def extend_schema(
        operation=None,
        operation_id=None,
        extra_parameters=None,
        responses=None,
        request=None,
        auth=None,
        description=None,
):
    """
    TODO some heavy explaining

    :param operation:
    :param operation_id:
    :param extra_parameters:
    :param responses:
    :param request:
    :param auth:
    :param description:
    :return:
    """

    def decorator(f):
        class ExtendedSchema(api_settings.DEFAULT_SCHEMA_CLASS):
            def get_operation(self, path, method, registry):
                if operation:
                    return operation
                return super().get_operation(path, method, registry)

            def get_operation_id(self, path, method):
                if operation_id:
                    return operation_id
                return super().get_operation_id(path, method)

            def get_extra_parameters(self, path, method):
                if extra_parameters:
                    return [
                        p.to_schema() if isinstance(p, OpenApiSchemaBase) else p
                        for p in extra_parameters
                    ]
                return super().get_extra_parameters(path, method)

            def get_auth(self, path, method):
                if auth:
                    return auth
                return super().get_auth(path, method)

            def get_request_serializer(self, path, method):
                if request:
                    return request
                return super().get_request_serializer(path, method)

            def get_response_serializers(self, path, method):
                if responses:
                    return responses
                return super().get_response_serializers(path, method)

            def get_description(self, path, method):
                if description:
                    return description
                return super().get_description(path, method)

        if inspect.isclass(f):
            class ExtendedView(f):
                schema = ExtendedSchema()

            return ExtendedView
        elif callable(f):
            # custom actions have kwargs in their context, others don't. create it so our create_view
            # implementation can overwrite the default schema
            if not hasattr(f, 'kwargs'):
                f.kwargs = {}

            # this simulates what @action is actually doing. somewhere along the line in this process
            # the schema is picked up from kwargs and used. it's involved my dear friends.
            f.kwargs['schema'] = ExtendedSchema()
            return f
        else:
            return f

    return decorator