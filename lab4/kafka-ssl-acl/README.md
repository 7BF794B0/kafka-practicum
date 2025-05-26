# Настройка защищённого соединения и управление доступом

## Инструкция по запуску

### 1. Запуск кластера Kafka с помощью Docker Compose

Для запуска кластера Kafka используйте Docker Compose. Выполните следующую команду:

```bash
docker-compose up -d
```

Эта команда запустит все необходимые сервисы в фоновом режиме.

### 2. Управление доступом

Создадим topic-1

```bash
docker exec -it kafka-1 kafka-topics --bootstrap-server kafka-1:9093 --topic topic-1 --create --partitions 3 --replication-factor 2 --command-config /tmp/admin.properties
```

Создадим topic-2

```bash
docker exec -it kafka-1 kafka-topics --bootstrap-server kafka-1:9093 --topic topic-2 --create --partitions 3 --replication-factor 2 --command-config /tmp/admin.properties
```

Проверим список топиков

```bash
docker exec -it kafka-1 kafka-topics --bootstrap-server kafka-1:9093 --command-config /tmp/admin.properties --list
```

Ожидаемый результат

```text
topic-1
topic-2
```

Создадим консольного продюсера в topic-1

```bash
docker exec -it kafka-1 kafka-console-producer --bootstrap-server kafka-1:9093 --topic topic-1 --producer.config /tmp/producer.properties
```

Попробуем отправить любое сообщение.
Ожидаемый результат

```text
org.apache.kafka.common.errors.TopicAuthorizationException: Not authorized to access topics: [topic-1]
```

Попробуем создать консольного консьюмера для topic-1

```bash
docker exec -it kafka-1 kafka-console-consumer --bootstrap-server kafka-1:9093 --topic topic-1 --consumer.config /tmp/consumer.properties --from-beginning
```

Ожидаемый результат

```text
org.apache.kafka.common.errors.TopicAuthorizationException: Not authorized to access topics: [topic-1]
```

Выдадим права для producer на запись в topic-1 и topic-2

```bash
docker exec -it kafka-1 kafka-acls --authorizer-properties zookeeper.connect=zookeeper:2181 --add --allow-principal User:producer --operation Write --topic topic-1
docker exec -it kafka-1 kafka-acls --authorizer-properties zookeeper.connect=zookeeper:2181 --add --allow-principal User:producer --operation Write --topic topic-2
```

Выдадим права для consumer на чтение topic-1, а на чтение topic-2 выдавать не будем

```bash
docker exec -it kafka-1 kafka-acls --authorizer-properties zookeeper.connect=zookeeper:2181 --add --allow-principal User:consumer --group consumer-group-1 --operation Read --topic topic-1
```

Создадим продюсеров для topic-1 и topic-2

```bash
docker exec -it kafka-1 kafka-console-producer --bootstrap-server kafka-1:9093 --topic topic-1 --producer.config /tmp/producer.properties
docker exec -it kafka-1 kafka-console-producer --bootstrap-server kafka-1:9093 --topic topic-2 --producer.config /tmp/producer.properties
```

Попробуем отправить сообщения. Ошибки авторизации быть не должно

Создадим консьюмеров для topic-1 и topic-2

```bash
docker exec -it kafka-1 kafka-console-consumer --bootstrap-server kafka-1:9093 --topic topic-1 --consumer.config /tmp/consumer.properties --from-beginning
```

Сообщения должны быть прочитаны

```bash
docker exec -it kafka-1 kafka-console-consumer --bootstrap-server kafka-1:9093 --topic topic-2 --consumer.config /tmp/consumer.properties --from-beginning
```

Так как для консьюмеров нет прав для чтения topic-2, то получим ошибку авторизации

```text
org.apache.kafka.common.errors.TopicAuthorizationException: Not authorized to access topics: [topic-2]
```
