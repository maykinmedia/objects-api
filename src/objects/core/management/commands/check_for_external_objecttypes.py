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
        external_uuids = set()
        for objecttype in ObjectType.objects.iterator():
            if not objecttype.is_imported:
                external_object_count += 1
                external_uuids.add(str(objecttype.uuid))

        msg = f"{external_object_count} objectype(s) have not been imported: {external_uuids}"

        if external_object_count > 0:
            self.stdout.write(self.style.ERROR(msg))
            raise CommandError(msg)
        else:
            self.stdout.write(self.style.SUCCESS("No external objecttypes found!"))
