from locust import TaskSet, task
from locust.contrib.fasthttp import FastHttpLocust


class UserBehavior(TaskSet):
    @task(1)
    def get_translate(self):
        self.client.get("/translate?text=hello")


class WebsiteUser(FastHttpLocust):
    task_set = UserBehavior
    min_wait = 1000
    max_wait = 1000
