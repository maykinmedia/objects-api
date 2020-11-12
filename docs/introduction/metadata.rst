Metadata
========

The Objecttypes API includes metadata which design is based on `Gezamenlijke aanpak Metadatabeheer
Data in de G4`_ and `Datacatalogus`_. The mapping for all Objecttypes attributes to fields from
these documents is shown in the table below.

========================   ==========================  =====================
Objecttypes attribute      Metadatabeheer              Datacatalogus
========================   ==========================  =====================
name                       A - Naam                    Titel
namePlural
description                                            Beschrijving
maintainerDepartment                                   Dienst
labels                     A - Trefwoorden             Tags
source                     B - Bronsysteem             Bron
versions/publicationDate   A - Wijzigingsdatum         Bijgewerkt
updateFrequency            A - Wijzigingsfrequentie    Updatefrequentie
maintainerOrganization     A - Eigenaar (Organisatie)  Eigenaar
contactPerson              A - Contactpersoon          Contactpersoon
contactEmail                                           E-mail contactpersoon
providerOrganization       A - Verstrekker             Verstrekker
status                     B - Huidige status          Status
dataClassification                                     Dataclassificatie
documentationUrl           C - Documentatie
========================   ==========================  =====================


.. _`Gezamenlijke aanpak Metadatabeheer Data in de G4`: https://github.com/maykinmedia/objects-api/files/5268978/Verplichte.metadatavelden.-.datacatalogus.docx

.. _`Datacatalogus`: https://github.com/maykinmedia/objects-api/files/5268978/Verplichte.metadatavelden.-.datacatalogus.docx
