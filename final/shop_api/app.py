import json
import time
import random

from typing import Iterable, Dict
from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient, Schema


class ShopAPI:
  def __init__(self, kafka_configs: Iterable[Dict]):
    """Create producers for all provided Kafka clusters."""
    self.producers = [Producer(cfg) for cfg in kafka_configs]
    self.products = self._load_products()
    self._register_schema()

  def _load_products(self):
    with open('products.json', 'r') as f:
      return json.load(f)

  def _register_schema(self):
    """Register product schema in Schema Registry."""
    client = SchemaRegistryClient({'url': 'http://schema-registry:8081'})
    with open('product.avsc', 'r') as schema_file:
      schema_str = schema_file.read()
    schema = Schema(schema_str, schema_type='AVRO')
    client.register_schema('products-value', schema)

  def delivery_report(self, err, msg):
    if err is not None:
      print(f'Message delivery failed: {err}')
    else:
      print(f'Message delivered to {msg.topic()} [{msg.partition()}]')

  def send_products(self):
    for product in self.products:
      # Добавляем случайное изменение цены и количества для демонстрации
      modified_product = product.copy()
      modified_product['price']['amount'] = round(product['price']['amount'] * random.uniform(0.9, 1.1), 2)
      modified_product['stock']['available'] = random.randint(0, product['stock']['available'] * 2)

      value = json.dumps(modified_product)
      for producer in self.producers:
        producer.produce(
          'products',
          key=modified_product['product_id'],
          value=value,
          callback=self.delivery_report,
        )

      for producer in self.producers:
        producer.flush()

      time.sleep(0.5)  # Задержка для имитации реального потока


if __name__ == '__main__':
  configs = [
    {
      'bootstrap.servers': 'kafka1:9093,kafka2:9094',
      'security.protocol': 'SSL',
      'ssl.ca.location': '/etc/kafka/secrets/ca-cert',
      'ssl.certificate.location': '/etc/kafka/secrets/kafka-cert',
      'ssl.key.location': '/etc/kafka/secrets/kafka-key',
      'acks': 'all',
      'enable.idempotence': 'true',
    },
    {
      'bootstrap.servers': 'kafka-backup1:9093,kafka-backup2:9094',
      'security.protocol': 'SSL',
      'ssl.ca.location': '/etc/kafka/secrets/ca-cert',
      'ssl.certificate.location': '/etc/kafka/secrets/kafka-cert',
      'ssl.key.location': '/etc/kafka/secrets/kafka-key',
      'acks': 'all',
      'enable.idempotence': 'true',
    }
  ]

  api = ShopAPI(configs)
  while True:
    api.send_products()
    time.sleep(60)  # Отправляем обновления каждую минуту
