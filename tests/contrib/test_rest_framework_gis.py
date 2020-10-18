from rest_framework import mixins, serializers, viewsets

try:
    from rest_framework_gis.fields import GeometryField, GeometrySerializerMethodField
except ImportError:
    GeometryField = object
    GeometrySerializerMethodField = object

from tests import assert_schema, generate_schema


class XSerializer(serializers.Serializer):
    location_method_field = GeometrySerializerMethodField()
    location_field = GeometryField()


class XViewset(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = XSerializer


def test_rest_framework_gis(no_warnings):
    assert_schema(
        generate_schema('x', XViewset),
        'tests/contrib/test_rest_framework_gis.yml'
    )
