from locust import HttpUser, task

OBJECTS_LIST = "/api/v2/objects"
AUTH_HEADERS = {"Authorization": "Token secret"}


class GetObjectsList(HttpUser):
    params = {
        "pageSize": 1000,
        "type": "http://localhost:8001/api/v2/objecttypes/f1220670-8ab7-44f1-a318-bd0782e97662",
        "data_attrs": "kiemjaar__exact__1234",
        "ordering": "-record__data__contactmoment__datumContact",
    }

    @task
    def get(self):
        self.client.get(OBJECTS_LIST, params=self.params, headers=AUTH_HEADERS)
