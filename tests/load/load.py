from locust import HttpUser, task, tag
from beeapi.api import apiconstants


class WebsiteUser(HttpUser):
    @tag("simple", "full")
    @task
    def choco_test(self):
        data = {
            "text": "chocolate cake"
        }

        self.client.post(apiconstants.JOBS_ENDPOINT, params=data)

    @tag("full")
    @task
    def velvet_test(self):
        data = {
            "text": "red velvet cake"
        }

        self.client.post(apiconstants.JOBS_ENDPOINT, params=data)

    @tag("full")
    @task
    def choc_and_velvet_test(self):
        data = {
            "text": "chocolate cake and red velvet cake"
        }

        self.client.post(apiconstants.JOBS_ENDPOINT, params=data)

