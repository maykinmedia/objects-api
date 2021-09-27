from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.urls import exceptions, reverse


class Command(BaseCommand):
    help = """
        Creates an initial superuser account, either:
            1) with an optionally specified password
            2) with an automatically generated password, mailing the credentials
               to a specified email address
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "username",
            help="Specifies the username for the superuser.",
        )

        # Cannot specify `required=True` here, because call_command cannot
        # deal with this: https://code.djangoproject.com/ticket/32047
        group = parser.add_mutually_exclusive_group(required=False)
        group.add_argument(
            "--email",
            action="store_true",
            help="Specifies the email for the superuser.",
        )
        group.add_argument(
            "--password",
            action="store_true",
            help="Specifies the password for the superuser.",
        )

    def handle(self, *args, **options):
        User = get_user_model()
        username = options["username"]
        email = options["email"]
        password = options["password"]

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING("Initial superuser already exists, doing nothing")
            )
            return

        if not password:
            password = User.objects.make_random_password(length=20)

        user = User.objects.create_superuser(
            username=username, email=email, password=password
        )

        if email:
            try:
                link = f'{settings.ALLOWED_HOSTS[0]}{reverse("admin:index")}'
            except IndexError:
                link = "unknown url"
            except exceptions.NoReverseMatch:
                link = settings.ALLOWED_HOSTS[0]

            send_mail(
                f"Credentials for {settings.PROJECT_NAME} ({link})",
                f"Credentials for project: {settings.PROJECT_NAME}\n\nUsername: {username}\nPassword: {password}",
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )

        self.stdout.write(self.style.SUCCESS("Initial superuser successfully created"))
