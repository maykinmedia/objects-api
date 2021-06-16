"""
This test suite asserts that the Objects API implementation supports
material and formal history defined in the StUF 03.01 (Standaard Uitwisseling Formaat)
https://www.gemmaonline.nl/images/gemmaonline/f/fa/Stuf0301.pdf
"""
from datetime import date

from rest_framework import status
from rest_framework.test import APITestCase

from objects.core.tests.factores import (
    ObjectFactory,
    ObjectRecordFactory,
    ObjectTypeFactory,
)
from objects.token.constants import PermissionModes
from objects.token.tests.factories import PermissionFactory
from objects.utils.test import TokenAuthMixin

from .utils import reverse

OBJECT_TYPES_API = "https://example.com/objecttypes/v1/"


class Stuf21Tests(TokenAuthMixin, APITestCase):
    """
    Test cases based on the Table 2.1 in the StUF 03.01
    |PersoonsId|volgnummer|geslachtsnaam|voorvoegsel|voorletters|geboortedatum|burgerlijkestaat|beginGeldigheid|
    |----------|----------|-------------|-----------|-----------|-------------|----------------|---------------|
    |5692      |1         |Poepenstaart |           |JP         |19770807     |ongehuwd        |19770807       |
    |5692      |40        |Bergh        |van den    |JP         |19770807     |ongehuwd        |20010903       |
    |5692      |50        |Bergh        |van den    |JP         |19770807     |gehuwd          |20050423       |
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.object_type = ObjectTypeFactory(service__api_root=OBJECT_TYPES_API)
        cls.object = ObjectFactory.create(object_type=cls.object_type)
        PermissionFactory.create(
            object_type=cls.object_type,
            mode=PermissionModes.read_and_write,
            token_auth=cls.token_auth,
        )

    def setUp(self):
        super().setUp()

        self.url = reverse("object-detail", args=[self.object.uuid])

    def test_1a_1_record_found(self):
        """
        Test 1a: If only record 1 (record with volgnummer=1) exists, material history
        and formal history on 01-01-2020 should say: Record 1
        """
        record_1 = ObjectRecordFactory.create(
            object=self.object,
            data={
                "geslachtsnaam": "Poepenstaart",
                "voorletters": "JP",
                "geboortedatum": "1977-08-07",
                "burgerlijkestaat": "ongehuwd",
            },
            start_at=date(1977, 8, 7),
            registration_at=date(1977, 8, 7),
        )

        material_response = self.client.get(self.url, {"date": "2020-01-01"})
        formal_response = self.client.get(self.url, {"registrationDate": "2020-01-01"})

        for response in [formal_response, material_response]:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.json()["url"], f"http://testserver{self.url}")
            self.assertEqual(response.json()["record"]["index"], record_1.index)

    def test_1b_1_record_not_found(self):
        """
        Test 1b: If only record 1 exists, material history and formal history
        on 01-01-1975 should say: No record.
        """
        ObjectRecordFactory.create(
            object=self.object,
            data={
                "geslachtsnaam": "Poepenstaart",
                "voorletters": "JP",
                "geboortedatum": "1977-08-07",
                "burgerlijkestaat": "ongehuwd",
            },
            start_at=date(1977, 8, 7),
            registration_at=date(1977, 8, 7),
        )

        material_response = self.client.get(self.url, {"date": "1975-01-01"})
        formal_response = self.client.get(self.url, {"registrationDate": "1975-01-01"})

        for response in [formal_response, material_response]:
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_2a_2_records_found(self):
        """
        Test 2a: If records 1 and 40 exists, material history and formal history on
        01-01-2020 should say: Record 40
        """
        record_1 = ObjectRecordFactory.create(
            object=self.object,
            data={
                "geslachtsnaam": "Poepenstaart",
                "voorletters": "JP",
                "geboortedatum": "1977-08-07",
                "burgerlijkestaat": "ongehuwd",
            },
            start_at=date(1977, 8, 7),
            end_at=date(2001, 9, 3),
            registration_at=date(1977, 8, 7),
        )
        record_40 = ObjectRecordFactory.create(
            object=self.object,
            data={
                "geslachtsnaam": "Bergh",
                "voorvoegsel": "van den",
                "voorletters": "JP",
                "geboortedatum": "1977-08-07",
                "burgerlijkestaat": "ongehuwd",
            },
            start_at=date(2001, 9, 3),
            registration_at=date(2001, 9, 3),
        )

        material_response = self.client.get(self.url, {"date": "2020-01-01"})
        formal_response = self.client.get(self.url, {"registrationDate": "2020-01-01"})

        for response in [formal_response, material_response]:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.json()["url"], f"http://testserver{self.url}")
            self.assertEqual(response.json()["record"]["index"], record_40.index)

    def test_2b_2_records_not_found(self):
        """
        Test 2b: If records 1 and 40 exists, material history and formal history
        on 01-01-1975 should say: No record.
        """
        ObjectRecordFactory.create(
            object=self.object,
            data={
                "geslachtsnaam": "Poepenstaart",
                "voorletters": "JP",
                "geboortedatum": "1977-08-07",
                "burgerlijkestaat": "ongehuwd",
            },
            start_at=date(1977, 8, 7),
            end_at=date(2001, 9, 3),
            registration_at=date(1977, 8, 7),
        )
        ObjectRecordFactory.create(
            object=self.object,
            data={
                "geslachtsnaam": "Bergh",
                "voorvoegsel": "van den",
                "voorletters": "JP",
                "geboortedatum": "1977-08-07",
                "burgerlijkestaat": "ongehuwd",
            },
            start_at=date(2001, 9, 3),
            registration_at=date(2001, 9, 3),
        )

        material_response = self.client.get(self.url, {"date": "1975-01-01"})
        formal_response = self.client.get(self.url, {"registrationDate": "1975-01-01"})

        for response in [formal_response, material_response]:
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_3a_3_records_found(self):
        """
        Test 3a: If records 1, 40 and 50 exists, material history and formal history
        on 01-01-2020 should say: Record 50
        """
        record_1 = ObjectRecordFactory.create(
            object=self.object,
            data={
                "geslachtsnaam": "Poepenstaart",
                "voorletters": "JP",
                "geboortedatum": "1977-08-07",
                "burgerlijkestaat": "ongehuwd",
            },
            start_at=date(1977, 8, 7),
            end_at=date(2001, 9, 3),
            registration_at=date(1977, 8, 7),
        )
        record_40 = ObjectRecordFactory.create(
            object=self.object,
            data={
                "geslachtsnaam": "Bergh",
                "voorvoegsel": "van den",
                "voorletters": "JP",
                "geboortedatum": "1977-08-07",
                "burgerlijkestaat": "ongehuwd",
            },
            start_at=date(2001, 9, 3),
            end_at=date(2005, 4, 23),
            registration_at=date(2001, 9, 3),
        )
        record_50 = ObjectRecordFactory.create(
            object=self.object,
            data={
                "geslachtsnaam": "Bergh",
                "voorvoegsel": "van den",
                "voorletters": "JP",
                "geboortedatum": "1977-08-07",
                "burgerlijkestaat": "gehuwd",
            },
            start_at=date(2005, 4, 23),
            registration_at=date(2005, 4, 23),
        )

        material_response = self.client.get(self.url, {"date": "2020-01-01"})
        formal_response = self.client.get(self.url, {"registrationDate": "2020-01-01"})

        for response in [formal_response, material_response]:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.json()["url"], f"http://testserver{self.url}")
            self.assertEqual(response.json()["record"]["index"], record_50.index)

    def test_3b_3_records_not_found(self):
        """
        Test 3b: If records 1, 40 and 50 exists, material history and formal history
        on 01-01-1975 should say: No record.
        """
        ObjectRecordFactory.create(
            object=self.object,
            data={
                "geslachtsnaam": "Poepenstaart",
                "voorletters": "JP",
                "geboortedatum": "1977-08-07",
                "burgerlijkestaat": "ongehuwd",
            },
            start_at=date(1977, 8, 7),
            end_at=date(2001, 9, 3),
            registration_at=date(1977, 8, 7),
        )
        ObjectRecordFactory.create(
            object=self.object,
            data={
                "geslachtsnaam": "Bergh",
                "voorvoegsel": "van den",
                "voorletters": "JP",
                "geboortedatum": "1977-08-07",
                "burgerlijkestaat": "ongehuwd",
            },
            start_at=date(2001, 9, 3),
            end_at=date(2005, 4, 23),
            registration_at=date(2001, 9, 3),
        )
        ObjectRecordFactory.create(
            object=self.object,
            data={
                "geslachtsnaam": "Bergh",
                "voorvoegsel": "van den",
                "voorletters": "JP",
                "geboortedatum": "1977-08-07",
                "burgerlijkestaat": "gehuwd",
            },
            start_at=date(2005, 4, 23),
            registration_at=date(2005, 4, 23),
        )

        material_response = self.client.get(self.url, {"date": "1975-01-01"})
        formal_response = self.client.get(self.url, {"registrationDate": "1975-01-01"})

        for response in [formal_response, material_response]:
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class Stuf22Tests(TokenAuthMixin, APITestCase):
    """
    Test cases based on the Table 2.2 in the StUF 03.01
    |PersoonsId|volgnummer|geslachtsnaam|voorvoegsel|voorletters|geboortedatum|burgerlijkestaat|beginGeldigheid|tijdstipRegistratie|
    |----------|----------|-------------|-----------|-----------|-------------|----------------|---------------|-------------------|
    |5692      |1         |Poepenstaart |           |JP         |19770807     |ongehuwd        |19770807       |19770815           |
    |5692      |10        |Berg         |van den    |JP         |19770807     |ongehuwd        |20010903       |20010910           |
    |5692      |40        |Bergh        |van den    |JP         |19770807     |ongehuwd        |20010903       |20011102           |
    |5692      |50        |Bergh        |van den    |JP         |19770807     |gehuwd          |20050423       |20050425           |
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.object_type = ObjectTypeFactory(service__api_root=OBJECT_TYPES_API)
        cls.object = ObjectFactory.create(object_type=cls.object_type)
        cls.record_1 = ObjectRecordFactory.create(
            object=cls.object,
            data={
                "geslachtsnaam": "Poepenstaart",
                "voorletters": "JP",
                "geboortedatum": "1977-08-07",
                "burgerlijkestaat": "ongehuwd",
            },
            start_at=date(1977, 8, 7),
            end_at=date(2001, 9, 3),
            registration_at=date(1977, 8, 15),
        )
        cls.record_10 = ObjectRecordFactory.create(
            object=cls.object,
            data={
                "geslachtsnaam": "Berg",
                "voorletters": "JP",
                "geboortedatum": "1977-08-07",
                "burgerlijkestaat": "ongehuwd",
            },
            start_at=date(2001, 9, 3),
            end_at=date(2001, 9, 3),
            registration_at=date(2001, 9, 10),
        )
        cls.record_40 = ObjectRecordFactory.create(
            object=cls.object,
            data={
                "geslachtsnaam": "Bergh",
                "voorvoegsel": "van den",
                "voorletters": "JP",
                "geboortedatum": "1977-08-07",
                "burgerlijkestaat": "ongehuwd",
            },
            start_at=date(2001, 9, 3),
            end_at=date(2005, 4, 23),
            registration_at=date(2001, 11, 2),
        )
        cls.record_50 = ObjectRecordFactory.create(
            object=cls.object,
            data={
                "geslachtsnaam": "Bergh",
                "voorvoegsel": "van den",
                "voorletters": "JP",
                "geboortedatum": "1977-08-07",
                "burgerlijkestaat": "gehuwd",
            },
            start_at=date(2005, 4, 23),
            registration_at=date(2005, 4, 25),
        )

        PermissionFactory.create(
            object_type=cls.object_type,
            mode=PermissionModes.read_and_write,
            token_auth=cls.token_auth,
        )

    def setUp(self):
        super().setUp()

        self.url = reverse("object-detail", args=[self.object.uuid])

    def test_4a_present(self):
        """
        Test 4a: material history and formal history on 01-01-2020 should say:
        Record 50
        """
        material_response = self.client.get(self.url, {"date": "2020-01-01"})
        formal_response = self.client.get(self.url, {"registrationDate": "2020-01-01"})

        for response in [formal_response, material_response]:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.json()["url"], f"http://testserver{self.url}")
            self.assertEqual(response.json()["record"]["index"], self.record_50.index)

    def test_4b_material_history(self):
        """
        Test 4b: material history on 01-10-2001 should say: Record 40
        """
        material_response = self.client.get(self.url, {"date": "2001-10-01"})

        self.assertEqual(material_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            material_response.json()["url"], f"http://testserver{self.url}"
        )
        self.assertEqual(
            material_response.json()["record"]["index"], self.record_40.index
        )

    def test_4c_formal_history(self):
        """
        Test 4c: formal history on 01-10-2001 should say: Record 10
        """
        format_response = self.client.get(self.url, {"registrationDate": "2001-10-01"})

        self.assertEqual(format_response.status_code, status.HTTP_200_OK)
        self.assertEqual(format_response.json()["url"], f"http://testserver{self.url}")
        self.assertEqual(
            format_response.json()["record"]["index"], self.record_10.index
        )

    def test_4d_not_found(self):
        """
        Test 4d: material history and formal history on 01-01-1975 should say:
        No record.
        """
        material_response = self.client.get(self.url, {"date": "1975-01-01"})
        formal_response = self.client.get(self.url, {"registrationDate": "1975-01-01"})

        for response in [formal_response, material_response]:
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class Stuf23Tests(TokenAuthMixin, APITestCase):
    """
    Test cases based on the Table 2.2 in the StUF 03.01
    |PersoonsId|volgnummer|geslachtsnaam|voorvoegsel|voorletters|geboortedatum|burgerlijkestaat|beginGeldigheid|tijdstipRegistratie|volgnrNaCorrectie|
    |----------|----------|-------------|-----------|-----------|-------------|----------------|---------------|-------------------|-----------------|
    |5692      |1         |Poepenstaart |           |JP         |19770807     |ongehuwd        |19770807       |19770815           |                 |
    |5692      |10        |Berg         |van den    |JP         |19770807     |ongehuwd        |20010903       |20010910           |40               |
    |5692      |40        |Bergh        |van den    |JP         |19770807     |ongehuwd        |20010903       |20011102           |                 |
    |5692      |50        |Bergh        |van den    |JP         |19770807     |gehuwd          |20050423       |20050425           |                 |
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.object_type = ObjectTypeFactory(service__api_root=OBJECT_TYPES_API)
        cls.object = ObjectFactory.create(object_type=cls.object_type)
        cls.record_1 = ObjectRecordFactory.create(
            object=cls.object,
            data={
                "geslachtsnaam": "Poepenstaart",
                "voorletters": "JP",
                "geboortedatum": "1977-08-07",
                "burgerlijkestaat": "ongehuwd",
            },
            start_at=date(1977, 8, 7),
            end_at=date(2001, 9, 3),
            registration_at=date(1977, 8, 15),
        )
        cls.record_10 = ObjectRecordFactory.create(
            object=cls.object,
            data={
                "geslachtsnaam": "Berg",
                "voorletters": "JP",
                "geboortedatum": "1977-08-07",
                "burgerlijkestaat": "ongehuwd",
            },
            start_at=date(2001, 9, 3),
            end_at=date(2001, 9, 3),
            registration_at=date(2001, 9, 10),
        )
        cls.record_40 = ObjectRecordFactory.create(
            object=cls.object,
            data={
                "geslachtsnaam": "Bergh",
                "voorvoegsel": "van den",
                "voorletters": "JP",
                "geboortedatum": "1977-08-07",
                "burgerlijkestaat": "ongehuwd",
            },
            start_at=date(2001, 9, 3),
            end_at=date(2005, 4, 23),
            registration_at=date(2001, 11, 2),
            correct=cls.record_10,
        )
        cls.record_50 = ObjectRecordFactory.create(
            object=cls.object,
            data={
                "geslachtsnaam": "Bergh",
                "voorvoegsel": "van den",
                "voorletters": "JP",
                "geboortedatum": "1977-08-07",
                "burgerlijkestaat": "gehuwd",
            },
            start_at=date(2005, 4, 23),
            registration_at=date(2005, 4, 25),
        )

        PermissionFactory.create(
            object_type=cls.object_type,
            mode=PermissionModes.read_and_write,
            token_auth=cls.token_auth,
        )

    def setUp(self):
        super().setUp()

        self.url = reverse("object-detail", args=[self.object.uuid])

    def test_5a_present(self):
        """
        Test 5a: material history and formal history on 01-01-2020 should say:
        Record 50
        """
        material_response = self.client.get(self.url, {"date": "2020-01-01"})
        formal_response = self.client.get(self.url, {"registrationDate": "2020-01-01"})

        for response in [formal_response, material_response]:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.json()["url"], f"http://testserver{self.url}")
            self.assertEqual(response.json()["record"]["index"], self.record_50.index)

    def test_5b_material_history(self):
        """
        Test 5b: material history on 01-10-2001 should say: Records 40.
        """
        material_response = self.client.get(self.url, {"date": "2001-10-01"})

        self.assertEqual(material_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            material_response.json()["url"], f"http://testserver{self.url}"
        )
        self.assertEqual(
            material_response.json()["record"]["index"], self.record_40.index
        )

    def test_5c_material_history(self):
        """
        Test 5c: material history on 04-09-2001 should say: Record 10.
        """
        material_response = self.client.get(self.url, {"date": "2001-09-04"})

        self.assertEqual(material_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            material_response.json()["url"], f"http://testserver{self.url}"
        )
        self.assertEqual(
            material_response.json()["record"]["index"], self.record_40.index
        )

    def test_5d_formal_history(self):
        """
        Test 5d: formal history on 01-10-2001 should say: Record 10
        """
        format_response = self.client.get(self.url, {"registrationDate": "2001-10-01"})

        self.assertEqual(format_response.status_code, status.HTTP_200_OK)
        self.assertEqual(format_response.json()["url"], f"http://testserver{self.url}")
        self.assertEqual(
            format_response.json()["record"]["index"], self.record_10.index
        )

    def test_5e_formal_history(self):
        """
        est 5e: formal history on 04-09-2001 should say: Record 40
        """
        format_response = self.client.get(self.url, {"registrationDate": "2001-09-04"})

        self.assertEqual(format_response.status_code, status.HTTP_200_OK)
        self.assertEqual(format_response.json()["url"], f"http://testserver{self.url}")
        self.assertEqual(format_response.json()["record"]["index"], self.record_1.index)

    def test_5f_not_found(self):
        """
        Test 4d: material history and formal history on 01-01-1975 should say:
        No record.
        """
        material_response = self.client.get(self.url, {"date": "1975-01-01"})
        formal_response = self.client.get(self.url, {"registrationDate": "1975-01-01"})

        for response in [formal_response, material_response]:
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
