from drf_spectacular.extensions import OpenApiSerializerFieldExtension
from drf_spectacular.plumbing import ResolvedComponent
from rest_framework_gis.serializers import GeometryField

geometry = ResolvedComponent(
    name="Geometry",
    type=ResolvedComponent.SCHEMA,
    object="Geometry",
    schema={
        "type": "object",
        "title": "Geometry",
        "description": "GeoJSON geometry",
        "required": ["type"],
        "externalDocs": {"url": "https://tools.ietf.org/html/rfc7946#section-3.1"},
        "properties": {
            "type": {
                "type": "string",
                "description": "The geometry type",
            }
        },
    },
)
point_2d = ResolvedComponent(
    name="Point2D",
    type=ResolvedComponent.SCHEMA,
    object="Point2D",
    schema={
        "type": "array",
        "title": "Point2D",
        "description": "A 2D point",
        "items": {"type": "number"},
        "maxItems": 2,
        "minItems": 2,
    },
)
point = ResolvedComponent(
    name="Point",
    type=ResolvedComponent.SCHEMA,
    object="Point",
    schema={
        "type": "object",
        "description": "GeoJSON point geometry",
        "externalDocs": {"url": "https://tools.ietf.org/html/rfc7946#section-3.1.2"},
        "allOf": [
            geometry.ref,
            {
                "type": "object",
                "required": ["coordinates"],
                "properties": {"coordinates": point_2d.ref},
            },
        ],
    },
)

multi_point = ResolvedComponent(
    name="MultiPoint",
    type=ResolvedComponent.SCHEMA,
    object="MultiPoint",
    schema={
        "type": "object",
        "description": "GeoJSON multi-point geometry",
        "externalDocs": {"url": "https://tools.ietf.org/html/rfc7946#section-3.1.3"},
        "allOf": [
            geometry.ref,
            {
                "type": "object",
                "required": ["coordinates"],
                "properties": {"coordinates": {"type": "array", "items": point_2d.ref}},
            },
        ],
    },
)

line_string = ResolvedComponent(
    name="LineString",
    type=ResolvedComponent.SCHEMA,
    object="LineString",
    schema={
        "type": "object",
        "description": "GeoJSON line-string geometry",
        "externalDocs": {"url": "https://tools.ietf.org/html/rfc7946#section-3.1.4"},
        "allOf": [
            geometry.ref,
            {
                "type": "object",
                "required": ["coordinates"],
                "properties": {
                    "coordinates": {
                        "type": "array",
                        "items": point_2d.ref,
                        "minItems": 2,
                    }
                },
            },
        ],
    },
)


multi_line_string = ResolvedComponent(
    name="MultiLineString",
    type=ResolvedComponent.SCHEMA,
    object="MultiLineString",
    schema={
        "type": "object",
        "description": "GeoJSON multi-line-string geometry",
        "externalDocs": {"url": "https://tools.ietf.org/html/rfc7946#section-3.1.5"},
        "allOf": [
            geometry.ref,
            {
                "type": "object",
                "required": ["coordinates"],
                "properties": {
                    "coordinates": {
                        "type": "array",
                        "items": {
                            "type": "array",
                            "items": point_2d.ref,
                        },
                    }
                },
            },
        ],
    },
)

polygon = ResolvedComponent(
    name="Polygon",
    type=ResolvedComponent.SCHEMA,
    object="Polygon",
    schema={
        "type": "object",
        "description": "GeoJSON polygon geometry",
        "externalDocs": {"url": "https://tools.ietf.org/html/rfc7946#section-3.1.6"},
        "allOf": [
            geometry.ref,
            {
                "type": "object",
                "required": ["coordinates"],
                "properties": {
                    "coordinates": {
                        "type": "array",
                        "items": {
                            "type": "array",
                            "items": point_2d.ref,
                        },
                    }
                },
            },
        ],
    },
)


multi_polygon = ResolvedComponent(
    name="MultiPolygon",
    type=ResolvedComponent.SCHEMA,
    object="MultiPolygon",
    schema={
        "type": "object",
        "description": "GeoJSON multi-polygon geometry",
        "externalDocs": {"url": "https://tools.ietf.org/html/rfc7946#section-3.1.7"},
        "allOf": [
            geometry.ref,
            {
                "type": "object",
                "required": ["coordinates"],
                "properties": {
                    "coordinates": {
                        "type": "array",
                        "items": {
                            "type": "array",
                            "items": {
                                "type": "array",
                                "items": point_2d.ref,
                            },
                        },
                    }
                },
            },
        ],
    },
)

geometry_collection = ResolvedComponent(
    name="GeometryCollection",
    type=ResolvedComponent.SCHEMA,
    object="GeometryCollection",
    schema={
        "type": "object",
        "description": "GeoJSON geometry collection",
        "externalDocs": {"url": "https://tools.ietf.org/html/rfc7946#section-3.1.8"},
        "allOf": [
            geometry.ref,
            {
                "type": "object",
                "required": ["geometries"],
                "properties": {"geometries": {"type": "array", "items": geometry.ref}},
            },
        ],
    },
)


class GeometryFieldExtension(OpenApiSerializerFieldExtension):
    target_class = GeometryField

    def get_name(self):
        return "GeoJSONGeometry"

    def map_serializer_field(self, auto_schema, direction):
        for component in [
            geometry,
            point_2d,
            point,
            multi_point,
            line_string,
            multi_line_string,
            polygon,
            multi_polygon,
            geometry_collection,
        ]:
            auto_schema.registry.register_on_missing(component)

        sub_components = [
            (component.name, component.ref)
            for component in [
                point,
                multi_point,
                line_string,
                multi_line_string,
                polygon,
                multi_polygon,
                geometry_collection,
            ]
        ]

        return {
            "oneOf": [ref for _, ref in sub_components],
            "discriminator": {
                "propertyName": "type",
                "mapping": {
                    resource_type: ref["$ref"] for resource_type, ref in sub_components
                },
            },
        }
