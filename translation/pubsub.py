import json

from kafka import KafkaConsumer


class Queue:
    def __init__(self, kafka):
        self.kafka = kafka

    @classmethod
    def initialize(cls, topic):
        kafka = KafkaConsumer(topic, bootstrap_servers="kafka:9092")
        return cls(kafka)

    def pull(self):
        while True:
            package = self.kafka.poll(timeout_ms=1000, max_records=50)
            for topic_partition, records in package.items():
                yield [json.loads(record.value.decode("utf-8")) for record in records]
