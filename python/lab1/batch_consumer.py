# batch_consumer.py
import json
import sys
from confluent_kafka import Consumer, KafkaError

def main():
    consumer_conf = {
        'bootstrap.servers': '127.0.0.1:9094,127.0.0.1:9095,127.0.0.1:9096',
        'group.id': 'batch-message-consumer-group',
        'auto.offset.reset': 'earliest',  # Если нет сохранённого оффсета, начинать с начала топика
        'enable.auto.commit': False       # Отключаем авто-коммит
    }

    consumer = Consumer(consumer_conf)
    consumer.subscribe(['my_topic'])

    print("BatchMessageConsumer started...")

    messages_batch = []
    batch_size = 10

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
                    print(f"[BatchConsumer] Error: {msg.error()}")
                    continue

            # Добавляем сообщения в список
            messages_batch.append(msg)

            # Проверяем, достигли ли нужного размера пакета
            if len(messages_batch) >= batch_size:
                # Обработка всех сообщений в батче
                try:
                    for m in messages_batch:
                        data = json.loads(m.value().decode('utf-8'))
                        print(f"[BatchConsumer] Processing: {data}")
                    # Когда всё успешно обработано, делаем единоразовый коммит
                    consumer.commit(asynchronous=False)
                except Exception as e:
                    # Если проблемы с десериализацией/обработкой
                    print(f"[BatchConsumer] Error in batch processing: {e}", file=sys.stderr)
                finally:
                    # Очищаем батч
                    messages_batch = []

    except KeyboardInterrupt:
        print("BatchMessageConsumer stopped by user")
    finally:
        consumer.close()

if __name__ == '__main__':
    main()
