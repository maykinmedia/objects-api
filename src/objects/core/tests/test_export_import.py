import json
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile

import hypothesis.strategies as st
import jsonschema_specifications
from hypothesis import HealthCheck, given, settings
from hypothesis.extra.django import TestCase, from_model
from hypothesis_jsonschema import from_schema

from ..import_export import export_data, import_data, import_upload
from ..models import ObjectType, ObjectTypeVersion
from ..utils import check_json_schema


def _valid_schema(json_value):
    try:
        check_json_schema(json_value)
    except Exception:
        return False
    else:
        # no escaped null-bytes PG JSONFields can't handle them
        return r"\u0000" not in json.dumps(json_value)


def jsonschemas():
    "Hypothesesis strategy that generates valid jsonschemata."
    # from_schema doesn't resolve $dynamicRef (yet), which the 2020 draft meta schema uses
    meta_schema = "https://json-schema.org/draft/2019-09/schema"
    return st.one_of(
        st.booleans(),
        st.just({}),
        (
            from_schema(
                jsonschema_specifications.REGISTRY[meta_schema].contents,  # type: ignore
            )
            .map(
                lambda schema: schema | {"$schema": meta_schema}
                if isinstance(schema, dict)
                else schema
            )
            .filter(_valid_schema)
        ),
    )


@st.composite
def objecttypes(
    draw: st.DrawFn, *, min_versions: int = 0, max_versions: int | None = None
) -> ObjectType:
    # postgres can't store

    object_type = draw(
        from_model(
            ObjectType,
            is_imported=st.just(False),
            contact_email=st.just("") | st.emails(),  # optional email
        )
    )
    # for better scr
    schemata = jsonschemas()
    schema = draw(schemata)

    # create some versions
    draw(
        st.lists(
            from_model(
                ObjectTypeVersion,
                object_type=st.just(object_type),
                json_schema=st.one_of(
                    st.just(schema),  # re-use same
                    schemata,  # change to a new schema
                ),
                # hypothesis infers the bounds correctly, but also tries 0
                # and will bump into the auto gen going out of bounds
                version=st.integers(min_value=1, max_value=(1 << 15) - 1),
            ),
            min_size=min_versions,
            max_size=max_versions,
        )
    )
    return object_type


class RoundTripExportImportTests(TestCase):
    def setup_example(self):
        # empty before each hypothesis example
        ObjectType.objects.all().delete()
        ObjectTypeVersion.objects.all().delete()
        return super().setup_example()

    @given(objecttypes=st.lists(objecttypes(max_versions=3), min_size=1, max_size=3))
    @settings(
        suppress_health_check=[HealthCheck.too_slow],
    )
    def test_export_import_roundtrip(self, objecttypes: list[ObjectType]) -> None:
        output = BytesIO()

        export_data(output, objecttypes=objecttypes)

        output.seek(0)

        original_versions = {
            ot.uuid: list(ot.versions.order_by("version")) for ot in objecttypes
        }

        # purge after export
        ObjectType.objects.all().delete()
        ObjectTypeVersion.objects.all().delete()

        import_data(output)

        assert ObjectType.objects.count() == len(objecttypes)

        imported_types = (
            ObjectType.objects.all().prefetch_related("versions").order_by("uuid")
        )
        assert imported_types.count() == len(objecttypes)

        for imported_type, original_type in zip(
            imported_types, sorted(objecttypes, key=lambda x: x.uuid)
        ):
            assert imported_type.is_imported is True

            assert imported_type.uuid == original_type.uuid
            assert imported_type.name == original_type.name.strip()
            assert imported_type.name_plural == original_type.name_plural.strip()
            assert imported_type.description == original_type.description.strip()
            assert (
                imported_type.data_classification
                == original_type.data_classification.strip()
            )
            assert (
                imported_type.maintainer_organization
                == original_type.maintainer_organization.strip()
            )
            assert (
                imported_type.maintainer_department
                == original_type.maintainer_department.strip()
            )
            assert imported_type.contact_person == original_type.contact_person.strip()
            assert imported_type.contact_email == original_type.contact_email.strip()
            assert imported_type.source == original_type.source.strip()
            assert (
                imported_type.update_frequency == original_type.update_frequency.strip()
            )
            assert (
                imported_type.provider_organization
                == original_type.provider_organization.strip()
            )
            assert (
                imported_type.documentation_url
                == original_type.documentation_url.strip()
            )
            assert imported_type.labels == original_type.labels
            assert imported_type.allow_geometry == original_type.allow_geometry

            assert imported_type.versions.count() == len(
                original_versions[original_type.uuid]
            )

            for imported_version, original_version in zip(
                imported_type.versions.order_by("version"),
                original_versions[original_type.uuid],
            ):
                assert imported_version.version == original_version.version
                assert imported_version.json_schema == original_version.json_schema
                assert imported_version.status == original_version.status
                assert imported_version.published_at == original_version.published_at

    @given(objecttype=objecttypes(min_versions=1, max_versions=3))
    @settings(
        suppress_health_check=[HealthCheck.too_slow],
    )
    def test_export_import_roundtrip_from_queryset(
        self, objecttype: ObjectType
    ) -> None:
        "Ensure a QuerySet[ObjectType] doesn't need an explicit prefect"
        num_versions = objecttype.versions.count()
        output = BytesIO()

        export_data(output, objecttypes=ObjectType.objects.all())

        output.seek(0)
        # purge after export
        ObjectType.objects.all().delete()
        ObjectTypeVersion.objects.all().delete()

        import_data(output)
        output.truncate()

        assert ObjectTypeVersion.objects.count() == num_versions

    @given(
        objecttypes=st.lists(
            objecttypes(min_versions=1, max_versions=3), min_size=1, max_size=3
        )
    )
    @settings(
        suppress_health_check=[HealthCheck.too_slow],
    )
    def test_export_import_with_new_uuids(self, objecttypes: list[ObjectType]) -> None:
        num_versions = ObjectTypeVersion.objects.count()
        output = BytesIO()

        export_data(output, objecttypes=objecttypes)

        output.seek(0)
        import_data(output, keep_uuid=False)
        output.truncate()

        assert ObjectType.objects.count() == len(objecttypes) * 2
        assert ObjectTypeVersion.objects.count() == num_versions * 2

    @given(objecttypes(min_versions=1, max_versions=3))
    @settings(suppress_health_check=[HealthCheck.too_slow])
    def test_export_import_with_new_uuid(self, original_type: ObjectType) -> None:
        output = BytesIO()

        export_data(output, objecttypes=[original_type])

        output.seek(0)
        # import a new, keeping original
        import_data(output, keep_uuid=False)
        output.truncate()

        imported_type = ObjectType.objects.exclude(uuid=original_type.uuid).get()

        assert imported_type.is_imported is True

        assert imported_type.uuid != original_type.uuid
        assert imported_type.name == original_type.name.strip()
        assert imported_type.name_plural == original_type.name_plural.strip()
        assert imported_type.description == original_type.description.strip()
        assert (
            imported_type.data_classification
            == original_type.data_classification.strip()
        )
        assert (
            imported_type.maintainer_organization
            == original_type.maintainer_organization.strip()
        )
        assert (
            imported_type.maintainer_department
            == original_type.maintainer_department.strip()
        )
        assert imported_type.contact_person == original_type.contact_person.strip()
        assert imported_type.contact_email == original_type.contact_email.strip()
        assert imported_type.source == original_type.source.strip()
        assert imported_type.update_frequency == original_type.update_frequency.strip()
        assert (
            imported_type.provider_organization
            == original_type.provider_organization.strip()
        )
        assert (
            imported_type.documentation_url == original_type.documentation_url.strip()
        )
        assert imported_type.labels == original_type.labels
        assert imported_type.allow_geometry == original_type.allow_geometry

        assert imported_type.versions.count() == original_type.versions.count()

        for imported_version, original_version in zip(
            imported_type.versions.order_by("version"),
            original_type.versions.order_by("version"),
        ):
            assert imported_version.version == original_version.version
            assert imported_version.json_schema == original_version.json_schema
            assert imported_version.status == original_version.status
            assert imported_version.published_at == original_version.published_at

    @given(objecttypes(), objecttypes())
    @settings(suppress_health_check=[HealthCheck.too_slow])
    def test_import_upload_list_of_files(self, ot1, ot2):
        output1 = BytesIO()
        output2 = BytesIO()

        export_data(output1, objecttypes=[ot1])
        export_data(output2, objecttypes=[ot2])

        file1 = SimpleUploadedFile(
            "file1.zip", output1.getvalue(), content_type="application/zip"
        )
        file2 = SimpleUploadedFile(
            "file2.zip", output2.getvalue(), content_type="application/zip"
        )

        ObjectType.objects.all().delete()

        errors = []

        def report_error(msg):
            errors.append(msg)

        import_upload([file1, file2], keep_uuid=True, report_error_to_user=report_error)

        assert set(ObjectType.objects.all().values_list("name", flat=True)) == {
            ot1.name.strip(),
            ot2.name.strip(),
        }
        assert errors == []
