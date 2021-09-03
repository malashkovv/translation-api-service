import json
import random

from locust import between, task
from locust.contrib.fasthttp import FastHttpUser

with open("/usr/src/app/quotes.json") as quotes_file:
    quotes = json.load(quotes_file)


class WebClient(FastHttpUser):

    wait_time = between(5, 10)

    @task
    def get_translation(self):
        random_quote = random.choice(quotes)["Quote"]
        self.client.get(f"/translate?text={random_quote}")
