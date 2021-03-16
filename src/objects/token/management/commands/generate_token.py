from django.core.management import BaseCommand
from django.utils.translation import ugettext_lazy as _

from objects.token.models import TokenAuth


class Command(BaseCommand):
    help = "Generate token with specified contact person, email and organization"

    def add_arguments(self, parser):
        parser.add_argument(
            "contact_person",
            help=_("Name of the contact person"),
        )
        parser.add_argument(
            "email",
            help=_("Email of the contact person"),
        )
        parser.add_argument(
            "--organization",
            default="",
            help=_("Name of the organization"),
        )
        parser.add_argument(
            "--application",
            default="",
            help=_("Name of the application"),
        )
        parser.add_argument(
            "--administration",
            default="",
            help=_("Name of the administration"),
        )

    def handle(self, *args, **options):
        contact_person = options["contact_person"]
        email = options["email"]
        organization = options["organization"]
        application = options["application"]
        administration = options["administration"]

        token_auth = TokenAuth.objects.create(
            contact_person=contact_person,
            email=email,
            organization=organization,
            application=application,
            administration=administration,
        )

        self.stdout.write("Token %s was generated" % token_auth.token)
