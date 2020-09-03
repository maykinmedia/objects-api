import jsonschema
import requests
from rest_framework import serializers

from objects.core.models import Object


class ObjectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Object
        fields = ("url", "type", "version", "data")
        extra_kwargs = {
            "url": {"lookup_field": "uuid"},
            "type": {"source": "object_type"},
        }
