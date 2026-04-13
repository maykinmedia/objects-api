from django.core.management import BaseCommand, CommandError

import structlog

from objects.core.models import ObjectType

logger = structlog.stdlib.get_logger(__name__)


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

        if external_object_count > 0:
            logger.warning("unimported_objecttypes", uuids=external_uuids)
            raise CommandError(
                f"{external_object_count} objectype(s) have not been imported: {', '.join(external_uuids)}"
            )
        else:
            self.stdout.write(self.style.SUCCESS("OK"))
