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

    def pull(self, timeout_ms=0, max_records=10):
        while True:
            package = self.kafka.poll(timeout_ms=timeout_ms, max_records=max_records)
            for topic_partition, records in package.items():
                yield [record.value.decode("utf-8") for record in records]
