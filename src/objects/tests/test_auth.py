from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from objects.core.tests.factores import ObjectFactory


class AuthTests(APITestCase):
    def test_non_auth(self):
        object = ObjectFactory.create()

        urls = [reverse("object-list"), reverse("object-detail", args=[object.uuid])]

        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
