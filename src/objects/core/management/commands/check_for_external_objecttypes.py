from django.core.management import BaseCommand, CommandError

from objects.core.models import ObjectType


class Command(BaseCommand):
    help = "Checks if external objecttypes exist"

    def _get_objecttype(self):
        """
        Separated for easier mocking
        """
        return ObjectType

    def handle(self, *args, **options):
        ObjectType = self._get_objecttype()

        external_object_count = 0
        service = set()
        for objecttype in ObjectType.objects.iterator():
            if not objecttype.is_imported:
                external_object_count += 1
                service.add(objecttype.service)

        msg = f"{external_object_count} objectypes have not been imported from the service(s): {service}"

        self.stdout.write(self.style.ERROR(msg))

        if external_object_count > 0:
            raise CommandError(msg)
