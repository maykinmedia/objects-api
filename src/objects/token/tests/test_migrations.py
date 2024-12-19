from django.core.management import call_command
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.db.migrations.state import StateApps
from django.test import TransactionTestCase


class BaseMigrationTest(TransactionTestCase):
    app: str
    migrate_from: str  # The migration before the one we want to test
    migrate_to: str  # The migration we want to test

    setting_overrides: dict = {}

    old_app_state: StateApps
    app_state: StateApps

    def setUp(self) -> None:
        """
        Setup the migration test by reversing to `migrate_from` state,
        then applying the `migrate_to` state.
        """
        assert self.app is not None, "You must define the `app` attribute"
        assert self.migrate_from is not None, "You must define `migrate_from`"
        assert self.migrate_to is not None, "You must define `migrate_to`"

        # Step 1: Set up the MigrationExecutor
        executor = MigrationExecutor(connection)

        # Step 2: Reverse to the starting migration state
        migrate_from = [(self.app, self.migrate_from)]
        old_migrate_state = executor.migrate(migrate_from)

        self.old_app_state = old_migrate_state.apps

    def _perform_migration(self) -> None:
        migrate_to = [(self.app, self.migrate_to)]

        executor = MigrationExecutor(connection)
        executor.loader.build_graph()  # reload the graph in case of dependency changes
        executor.migrate(migrate_to)

        self.apps = executor.loader.project_state(migrate_to).apps

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()

        # reset to latest migration
        call_command("migrate", verbosity=0, database=connection._alias)


class TestTokenAuthUniqueness(BaseMigrationTest):
    app = "token"
    migrate_from = "0016_alter_permission_token_auth"
    migrate_to = "0017_tokenauth_identifier_alter_tokenauth_token"

    def test_migrate_tokens_check_attr(self):
        TokenAuth = self.old_app_state.get_model("token", "TokenAuth")
        self.assertFalse(hasattr(TokenAuth, "identifier"))

        self._perform_migration()

        TokenAuth = self.apps.get_model("token", "TokenAuth")
        self.assertTrue(hasattr(TokenAuth, "identifier"))

    def test_migrate_tokens_to_unique_identifiers(self):
        TokenAuth = self.old_app_state.get_model("token", "TokenAuth")
        TokenAuth.objects.create(
            token="aa018d1c576c9dae33be1e549f739f2834ebc811",
            contact_person="Person 1",
            email="test@example.com",
        )
        TokenAuth.objects.create(
            token="ab700d6bf906c2b4b42a961c529657314c6a8246",
            contact_person="Other person",
            email="somebody@else.com",
        )

        self._perform_migration()

        TokenAuth = self.apps.get_model("token", "TokenAuth")
        tokens = TokenAuth.objects.all()
        self.assertEqual(tokens.count(), 2)

        first_token = tokens.get(token="aa018d1c576c9dae33be1e549f739f2834ebc811")
        second_token = tokens.get(token="ab700d6bf906c2b4b42a961c529657314c6a8246")
        self.assertNotEqual(first_token.identifier, second_token.identifier)
