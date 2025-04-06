# single_consumer.py
import json
import sys
from confluent_kafka import Consumer, KafkaError

def main():
    consumer_conf = {
        'bootstrap.servers': '127.0.0.1:9094,127.0.0.1:9095,127.0.0.1:9096',
        'group.id': 'single-message-consumer-group',
        'auto.offset.reset': 'earliest',      # Если нет сохранённого оффсета, начинать с начала топика
        'enable.auto.commit': True            # Автоматический коммит
    }

    consumer = Consumer(consumer_conf)
    consumer.subscribe(['my_topic'])

    print("SingleMessageConsumer started...")

    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue  # нет сообщений – ждём дальше
            if msg.error():
                # Если пришла ошибка, просто логируем
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # Достигнут конец партиции
                    continue
                else:
                    print(f"[SingleConsumer] Error: {msg.error()}")
                    continue

            # Пробуем десериализовать
            try:
                data = json.loads(msg.value().decode('utf-8'))
                print(f"[SingleConsumer] Received message: {data}")
            except Exception as e:
                print(f"[SingleConsumer] Deserialization error: {e}", file=sys.stderr)

    except KeyboardInterrupt:
        print("SingleMessageConsumer stopped by user")
    finally:
        consumer.close()

if __name__ == '__main__':
    main()
