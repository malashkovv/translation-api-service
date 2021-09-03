import json

from kafka import KafkaConsumer


class Queue:
    def __init__(self, kafka):
        self.kafka = kafka

    @classmethod
    def initialize(cls, urls, topic):
        kafka = KafkaConsumer(
            topic, bootstrap_servers=urls, group_id=f"translator_for_{topic}"
        )
        return cls(kafka)

    def pull(self):
        while True:
            package = self.kafka.poll(timeout_ms=200, max_records=25)
            for topic_partition, records in package.items():
                yield [json.loads(record.value.decode("utf-8")) for record in records]
