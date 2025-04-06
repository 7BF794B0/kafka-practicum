# producer.py
import json
import time
from confluent_kafka import Producer

class MyMessage:
    """Простейший класс для примера сериализации."""
    def __init__(self, msg_id, text):
        self.msg_id = msg_id
        self.text = text

def main():
    # Настройки продюсера
    # "acks=all" даёт гарантию "at least once" при условии, что консюмер корректно коммитит оффсеты.
    producer_conf = {
        'bootstrap.servers': '127.0.0.1:9094,127.0.0.1:9095,127.0.0.1:9096',
        'acks': 'all',
    }
    producer = Producer(producer_conf)

    def delivery_report(err, msg):
        """Callback, вызывается при подтверждении (или ошибке) доставки сообщения брокером."""
        if err is not None:
            print(f"Delivery failed for message {msg.key()}: {err}")
        else:
            print(f"Message delivered to {msg.topic()} [{msg.partition()}] @ offset {msg.offset()}")

    # Отправим тестовые сообщения
    for i in range(30):
        # Генерируем объект сообщения
        message_object = MyMessage(i, f"Hello from python producer, index={i}")
        try:
            # Сериализуем в JSON
            serialized_value = json.dumps(message_object.__dict__).encode('utf-8')
            # Логируем, что отправляем
            print(f"Sending: {message_object.__dict__}")

            producer.produce(
                topic='my_topic',
                value=serialized_value,
                on_delivery=delivery_report
            )
        except Exception as e:
            print(f"[Producer] Error while serializing or sending message: {e}")

        time.sleep(1)

    # Ждём окончания отправки всех сообщений
    producer.flush()

if __name__ == '__main__':
    main()
