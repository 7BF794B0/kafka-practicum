from confluent_kafka import Consumer, KafkaException

conf = {
    'bootstrap.servers': '127.0.0.1:9094,127.0.0.1:9095,127.0.0.1:9096',
    'group.id': 'python-consumer',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': True
}

consumer = Consumer(conf)
consumer.subscribe(['postgres.public.users', 'postgres.public.orders'])

print("⏳ Ожидание сообщений...")
try:
    while True:
        msg = consumer.poll(timeout=1.0)
        if msg is None:
          continue  # нет сообщений – ждём дальше
        if msg.error():
            raise KafkaException(msg.error())
        print(f"\n📥 Новое сообщение в топике {msg.topic()}:")
        print(msg.value().decode('utf-8'))
except KeyboardInterrupt:
    pass
finally:
    consumer.close()
