from rest_framework import viewsets

from objects.core.models import Object

from .serializers import ObjectSerializer


class ObjectViewSet(viewsets.ModelViewSet):
    queryset = Object.objects.order_by("-pk")
    serializer_class = ObjectSerializer
    lookup_field = "uuid"
