from rest_framework import viewsets
from .models import Object
from .serializers import ObjectSerializer


class ObjectViewSet(viewsets.ModelViewSet):
    queryset = Object.objects.all()
    serializer_class = ObjectSerializer
