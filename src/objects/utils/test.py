from rest_framework.authtoken.models import Token

from objects.accounts.models import User


class TokenAuthMixin:
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.user = User.objects.create(username="testsuite", password="letmein")
        cls.token = Token.objects.create(user=cls.user)

    def setUp(self):
        super().setUp()

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token}")
