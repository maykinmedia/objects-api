from pathlib import Path

from django.contrib.sites.models import Site
from django.db.models import QuerySet
from django.test import TestCase

from django_setup_configuration.exceptions import ConfigurationRunFailed
from django_setup_configuration.test_utils import execute_single_step

from objects.setup_configuration.steps.sites import SitesConfigurationStep

TEST_FILES = (Path(__file__).parent / "files").resolve()


class SitesConfigurationStepTests(TestCase):
    def test_empty_database(self):
        test_file_path = str(TEST_FILES / "sites_empty_database.yaml")

        execute_single_step(SitesConfigurationStep, yaml_source=test_file_path)

        sites: QuerySet[Site] = Site.objects.all()

        self.assertEqual(sites.count(), 2)

        example_site: Site = sites.get(name="Example site")
        self.assertEqual(example_site.domain, "example.com")

        alternative_site: Site = sites.get(name="Alternative example site")
        self.assertEqual(alternative_site.domain, "alternative.example.com")

    def test_existing_sites(self):
        test_file_path = str(TEST_FILES / "sites_existing_sites.yaml")

        example_site, _ = Site.objects.get_or_create(
            domain="example.com", defaults=dict(name="Example site")
        )

        alternative_site = Site.objects.create(
            domain="alternative.example.com",
            name="Alternative example site",
        )

        execute_single_step(SitesConfigurationStep, yaml_source=test_file_path)

        sites: QuerySet[Site] = Site.objects.order_by("name")

        self.assertEqual(sites.count(), 3)

        example_site: Site = sites.get(name="Example site (revised)")
        self.assertEqual(example_site.domain, "example.com")

        alternative_site: Site = sites.get(name="Alternative example site")
        self.assertEqual(alternative_site.domain, "alternative.example.com")

        test_site: Site = sites.get(name="Test site")
        self.assertEqual(test_site.domain, "test.example.com")

    def test_invalid_domain(self):
        test_file_path = str(TEST_FILES / "sites_invalid_domain.yaml")

        with self.assertRaises(ConfigurationRunFailed):
            execute_single_step(SitesConfigurationStep, yaml_source=test_file_path)

        sites: QuerySet[Site] = Site.objects.all()

        # the default test site created during test runs
        self.assertEqual(sites.count(), 1)

        site: Site = sites.get()

        self.assertEqual(site.domain, "example.com")

    def test_idempotent_step(self):
        test_file_path = str(TEST_FILES / "sites_idempotent_step.yaml")

        execute_single_step(SitesConfigurationStep, yaml_source=test_file_path)

        sites: QuerySet[Site] = Site.objects.all()

        self.assertEqual(sites.count(), 2)

        example_site: Site = sites.get(name="Example site")
        self.assertEqual(example_site.domain, "example.com")

        alternative_site: Site = sites.get(name="Alternative example site")
        self.assertEqual(alternative_site.domain, "alternative.example.com")

        execute_single_step(SitesConfigurationStep, yaml_source=test_file_path)

        self.assertEqual(Site.objects.count(), 2)

        example_site.refresh_from_db()

        self.assertEqual(example_site.name, "Example site")
        self.assertEqual(example_site.domain, "example.com")

        alternative_site.refresh_from_db()

        self.assertEqual(alternative_site.name, "Alternative example site")
        self.assertEqual(alternative_site.domain, "alternative.example.com")
