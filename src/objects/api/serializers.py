from rest_framework import serializers

from .models import Object


class ObjectSerializer(serializers.HyperlinkedModelSerializer):
    model = Object
    fields = ("type", "version", "data")
    extra_kwargs = {
        "type": {"source": "object_type"},
    }
