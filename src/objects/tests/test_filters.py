from django.urls import reverse, reverse_lazy

from rest_framework import status
from rest_framework.test import APITestCase

from objects.core.tests.factores import ObjectFactory

OBJECT_TYPE = "https://example.com/objecttypes/v1/types/a6c109"


class FilterTests(APITestCase):
    url = reverse_lazy("object-list")

    def test_filter_object_type(self):
        object = ObjectFactory.create(object_type=OBJECT_TYPE)
        ObjectFactory.create()

        response = self.client.get(self.url, {"type": OBJECT_TYPE})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["url"],
            f"http://testserver{reverse('object-detail', args=[object.uuid])}",
        )
