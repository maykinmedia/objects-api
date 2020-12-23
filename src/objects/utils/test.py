from objects.token.tests.factories import TokenAuthFactory


class TokenAuthMixin:
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.token_auth = TokenAuthFactory(
            contact_person="testsuite", email="test@letmein.nl"
        )

    def setUp(self):
        super().setUp()

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token_auth.token}")
