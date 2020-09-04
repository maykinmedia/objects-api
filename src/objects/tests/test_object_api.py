from django.urls import reverse

from rest_framework.test import APITestCase

from objects.core.tests.factores import ObjectFactory, ObjectRecordFactory


class ObjectApiTests(APITestCase):
    def test_retrieve_object(self):
        object = ObjectFactory.create()
        ObjectRecordFactory.create(object=object)
        url = reverse("object-detail", args=[object.uuid])

        response = self.client.get(url)

        print(response)
        print(response.json())
