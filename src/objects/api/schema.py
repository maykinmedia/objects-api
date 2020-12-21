from django.conf import settings

from drf_yasg import openapi

description = """An API to manage Objects.

# Introduction

An OBJECT is of a certain OBJECTTYPE (defined in the Objecttypes API). An 
OBJECT has a few core attributes that every OBJECT (technically a RECORD,
see below) has, although these attribtutes can sometimes be empty. They are
attributes like `geometry` and some administrative attributes. The data that
describes the actual object is stored in the `data` attribute and follows 
the JSON schema as given by the OBJECTTYPE.

## History

Each OBJECT has 1 or more RECORDs. A RECORD contains the data of an OBJECT 
at a certain time. An OBJECT can have multiple RECORDS that decribe the 
history of that OBJECT. Changes to an OBJECT actually create a new RECORD 
under the OBJECT and leaves the old RECORD as is.

Over time, an OBJECTTYPE can also change. This is reflected with 
OBJECTTYPE-VERSIONs. Therefore, a RECORD always indicates which 
OBJECTTYPE-VERSION it uses described by the `OBJECT.type` and 
`RECORD.typeVersion` attributes.

### Material and formal history

History can be seen from 2 perspectives: formal and material history. The 
formal history describes the history as it should be (stored in the 
`startAt` and `endAt` attributes). The material history describes the 
history as it was administratively processed (stored in the `registeredAt`
attribute).

The difference is that an object could be created or updated in the real 
world at a certain point in time but the administrative change (ie. save or
update the object in the Objects API) can be done at a later time. The
query parameters `?date=2021-01-01` (formal history) and 
`?registrationDate=2021-01-01` (material history) allow for querying the 
RECORDS as seen from both perspectives, and can yield different results.

### Corrections

RECORDs cannot be deleted or changed once saved. If an error was made to
a RECORD, the RECORD can be "corrected" by saving a new RECORD and indicate
that it corrects a previous RECORD. This is done via the attribute 
`correctionFor`.

### Deletion

Although OBJECTs can be deleted, it is sometimes better to set the 
`endDate` of an OBJECT. Deleting an OBJECT also deletes all RECORDs in 
accordance with privacy laws.

# Authorizations

The API uses API-tokens that grant certain permissions. The API-token is
passed via a header, like this: `Authorization: Token <token>`
"""

info = openapi.Info(
    title=f"{settings.PROJECT_NAME} API",
    default_version=settings.API_VERSION,
    description=description,
)
