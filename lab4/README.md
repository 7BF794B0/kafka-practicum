# 📊 Балансировка партиций и диагностика кластера Kafka

## 🔧 Используемая среда

* Docker Compose с 3 брокерами Kafka (bitnami/kafka:3.4) и Kafka-UI (provectuslabs/kafka-ui).
* KRaft mode (без ZooKeeper).
* Kafka-UI на `localhost:8080`.

## ✅ Шаг 1: Создание топика

```bash
docker exec -it kafka-1 kafka-topics.sh --create --topic balanced_topic --partitions 8 --replication-factor 3 --bootstrap-server kafka-1:9092
```

### Результат:

```text
Created topic balanced_topic.
```

---

## 📊 Шаг 2: Определение текущего распределения партиций

```bash
docker exec -it kafka-1 kafka-topics.sh --describe --topic balanced_topic --bootstrap-server kafka-1:9092
```

### Результат:

```text
Topic: balanced_topic   TopicId: cQctRO5ASP2W_m4qvCOh4Q PartitionCount: 8       ReplicationFactor: 3    Configs:
        Topic: balanced_topic   Partition: 0    Leader: 2       Replicas: 2,3,1 Isr: 2,3,1
        Topic: balanced_topic   Partition: 1    Leader: 3       Replicas: 3,1,2 Isr: 3,1,2
        Topic: balanced_topic   Partition: 2    Leader: 1       Replicas: 1,2,3 Isr: 1,2,3
        Topic: balanced_topic   Partition: 3    Leader: 1       Replicas: 1,3,2 Isr: 1,3,2
        Topic: balanced_topic   Partition: 4    Leader: 3       Replicas: 3,2,1 Isr: 3,2,1
        Topic: balanced_topic   Partition: 5    Leader: 2       Replicas: 2,1,3 Isr: 2,1,3
        Topic: balanced_topic   Partition: 6    Leader: 2       Replicas: 2,1,3 Isr: 2,1,3
        Topic: balanced_topic   Partition: 7    Leader: 1       Replicas: 1,3,2 Isr: 1,3,2
```

---

## 🛠️ Шаг 3: Подготовка reassignment.json

Создаём `reassignment.json`:

```json
{
  "partitions": [
    { "topic": "balanced_topic", "partition": 0, "replicas": [2, 3, 1] },
    { "topic": "balanced_topic", "partition": 1, "replicas": [3, 1, 2] },
    { "topic": "balanced_topic", "partition": 2, "replicas": [1, 2, 3] },
    { "topic": "balanced_topic", "partition": 3, "replicas": [2, 1, 3] },
    { "topic": "balanced_topic", "partition": 4, "replicas": [3, 2, 1] },
    { "topic": "balanced_topic", "partition": 5, "replicas": [1, 3, 2] },
    { "topic": "balanced_topic", "partition": 6, "replicas": [2, 1, 3] },
    { "topic": "balanced_topic", "partition": 7, "replicas": [3, 2, 1] }
  ]
}
```

---

## 📦 Шаг 4: Перераспределение партиций

```bash
docker cp reassignment.json kafka-1:/tmp/reassignment.json
docker exec -it kafka-1 kafka-reassign-partitions.sh --bootstrap-server kafka-1:9092 --reassignment-json-file /tmp/reassignment.json --execute
```

### Результат:

```text
Successfully copied 2.56kB to kafka-1:/tmp/reassignment.json
Current partition replica assignment

{"version":1,"partitions":[{"topic":"balanced_topic","partition":0,"replicas":[2,3,1],"log_dirs":["any","any","any"]},{"topic":"balanced_topic","partition":1,"replicas":[3,1,2],"log_dirs":["any","any","any"]},{"topic":"balanced_topic","partition":2,"replicas":[1,2,3],"log_dirs":["any","any","any"]},{"topic":"balanced_topic","partition":3,"replicas":[1,3,2],"log_dirs":["any","any","any"]},{"topic":"balanced_topic","partition":4,"replicas":[3,2,1],"log_dirs":["any","any","any"]},{"topic":"balanced_topic","partition":5,"replicas":[2,1,3],"log_dirs":["any","any","any"]},{"topic":"balanced_topic","partition":6,"replicas":[2,1,3],"log_dirs":["any","any","any"]},{"topic":"balanced_topic","partition":7,"replicas":[1,3,2],"log_dirs":["any","any","any"]}]}

Save this to use as the --reassignment-json-file option during rollback
Successfully started partition reassignments for balanced_topic-0,balanced_topic-1,balanced_topic-2,balanced_topic-3,balanced_topic-4,balanced_topic-5,balanced_topic-6,balanced_topic-7
```

---

## 📈 Шаг 5: Проверка статуса перераспределения

```bash
docker exec -it kafka-1 kafka-reassign-partitions.sh --bootstrap-server kafka-1:9092 --reassignment-json-file /tmp/reassignment.json --verify
```

### Результат:

```text
Status of partition reassignment:
Reassignment of partition balanced_topic-0 is completed.
Reassignment of partition balanced_topic-1 is completed.
Reassignment of partition balanced_topic-2 is completed.
Reassignment of partition balanced_topic-3 is completed.
Reassignment of partition balanced_topic-4 is completed.
Reassignment of partition balanced_topic-5 is completed.
Reassignment of partition balanced_topic-6 is completed.
Reassignment of partition balanced_topic-7 is completed.

Clearing broker-level throttles on brokers 1,2,3
Clearing topic-level throttles on topic balanced_topic
```

---

## 🔁 Шаг 6: Проверка обновлённой конфигурации

```bash
docker exec -it kafka-1 kafka-topics.sh --describe --topic balanced_topic --bootstrap-server kafka-1:9092
```

### Результат:

```text
Topic: balanced_topic   TopicId: cQctRO5ASP2W_m4qvCOh4Q PartitionCount: 8       ReplicationFactor: 3    Configs:
        Topic: balanced_topic   Partition: 0    Leader: 2       Replicas: 2,3,1 Isr: 2,3,1
        Topic: balanced_topic   Partition: 1    Leader: 3       Replicas: 3,1,2 Isr: 3,1,2
        Topic: balanced_topic   Partition: 2    Leader: 1       Replicas: 1,2,3 Isr: 1,2,3
        Topic: balanced_topic   Partition: 3    Leader: 1       Replicas: 2,1,3 Isr: 1,3,2
        Topic: balanced_topic   Partition: 4    Leader: 3       Replicas: 3,2,1 Isr: 3,2,1
        Topic: balanced_topic   Partition: 5    Leader: 2       Replicas: 1,3,2 Isr: 2,1,3
        Topic: balanced_topic   Partition: 6    Leader: 2       Replicas: 2,1,3 Isr: 2,1,3
        Topic: balanced_topic   Partition: 7    Leader: 1       Replicas: 3,2,1 Isr: 1,3,2
```

---

## 💣 Шаг 7: Симуляция сбоя

### a. Остановить `kafka-1`:

```bash
docker stop kafka-1
```

### b. Проверка состояния топика:

```bash
docker exec -it kafka-2 kafka-topics.sh --describe --topic balanced_topic --bootstrap-server kafka-2:9092
```

* Проверили, какие партиции лишились лидера.
* Некоторые партиции могли быть временно недоступны или иметь неполный ISR.

### Результат:

```text
Topic: balanced_topic   TopicId: cQctRO5ASP2W_m4qvCOh4Q PartitionCount: 8       ReplicationFactor: 3    Configs:
        Topic: balanced_topic   Partition: 0    Leader: 2       Replicas: 2,3,1 Isr: 2,3
        Topic: balanced_topic   Partition: 1    Leader: 3       Replicas: 3,1,2 Isr: 3,2
        Topic: balanced_topic   Partition: 2    Leader: 2       Replicas: 1,2,3 Isr: 2,3
        Topic: balanced_topic   Partition: 3    Leader: 2       Replicas: 2,1,3 Isr: 3,2
        Topic: balanced_topic   Partition: 4    Leader: 3       Replicas: 3,2,1 Isr: 3,2
        Topic: balanced_topic   Partition: 5    Leader: 3       Replicas: 1,3,2 Isr: 2,3
        Topic: balanced_topic   Partition: 6    Leader: 2       Replicas: 2,1,3 Isr: 2,3
        Topic: balanced_topic   Partition: 7    Leader: 3       Replicas: 3,2,1 Isr: 3,2
```

---

### c. Запуск `kafka-1` обратно:

```bash
docker start kafka-1
```

### d. Проверка восстановления ISR:

```bash
docker exec -it kafka-1 kafka-topics.sh --describe --topic balanced_topic --bootstrap-server kafka-1:9092
```

### Результат:

```text
Topic: balanced_topic   TopicId: cQctRO5ASP2W_m4qvCOh4Q PartitionCount: 8       ReplicationFactor: 3    Configs:
        Topic: balanced_topic   Partition: 0    Leader: 2       Replicas: 2,3,1 Isr: 2,3,1
        Topic: balanced_topic   Partition: 1    Leader: 3       Replicas: 3,1,2 Isr: 3,2,1
        Topic: balanced_topic   Partition: 2    Leader: 2       Replicas: 1,2,3 Isr: 2,3,1
        Topic: balanced_topic   Partition: 3    Leader: 2       Replicas: 2,1,3 Isr: 3,2,1
        Topic: balanced_topic   Partition: 4    Leader: 3       Replicas: 3,2,1 Isr: 3,2,1
        Topic: balanced_topic   Partition: 5    Leader: 3       Replicas: 1,3,2 Isr: 2,3,1
        Topic: balanced_topic   Partition: 6    Leader: 2       Replicas: 2,1,3 Isr: 2,3,1
        Topic: balanced_topic   Partition: 7    Leader: 3       Replicas: 3,2,1 Isr: 3,2,1
```

---

## 🧠 Выводы

* Перераспределение партиций прошло успешно, что позволяет равномерно распределить нагрузку между брокерами.
* В случае сбоя одного из брокеров кластер продолжал работу, хотя часть партиций временно теряла лидеров.
* После восстановления сбойного брокера реплики синхронизировались автоматически.
* Инструмент `kafka-reassign-partitions.sh` полезен для ручной балансировки, особенно когда автоматика не справляется.
