from django.urls import include, path

urlpatterns = [
    path("v2", include("objects.api.v2.urls", namespace="v2")),
]
