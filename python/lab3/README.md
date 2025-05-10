Проект состоит из следующих компонентов:

1. PostgreSQL - источник данных с таблицами users и orders
2. Apache Kafka - брокер сообщений для передачи изменений данных
3. Kafka Connect с Debezium - для захвата изменений из PostgreSQL (CDC)
4. Prometheus - система сбора и хранения метрик
5. Grafana - для визуализации метрик
6. Python consumer - консумер, который подписывается на сообщения, которые захватываются Debezium

Структура проекта:

```bash
.
├── confluent-hub-components
│   ├── debezium-api-3.1.1.Final.jar
│   ├── debezium-connector-postgres-3.1.1.Final.jar
│   ├── debezium-core-3.1.1.Final.jar
│   ├── postgresql-42.6.1.jar
│   └── protobuf-java-3.25.5.jar
├── connectors
│   └── debezium-postgres-connector.json
├── consumer
│   └── kafka_consumer.py
├── create-db.sql
├── docker-compose.yaml
├── insert.sql
├── jmx-exporter
│   ├── 14845_rev5.json
│   ├── jmx_prometheus_javaagent-1.0.1.jar
│   └── kafka-jmx-metric.yaml
├── postgresql.conf
├── prometheus
│   └── prometheus.yml
└── README.md
```

Инструкция по запуску:

1. Запуск сервисов:

```bash
docker-compose up -d

```

2. Создание Debezium коннектора:

```bash
curl -i -X POST -H "Accept:application/json" -H "Content-Type:application/json" http://localhost:8083/connectors/ -d @connectors/debezium-postgres-connector.json
```

3. Проверка статус коннектора:

```bash
curl -s http://localhost:8083/connectors/postgres-connector/status | jq
```

Ответ:

```bash
{
  "name": "postgres-connector",
  "connector": {
    "state": "RUNNING",
    "worker_id": "172.18.0.7:8083"
  },
  "tasks": [
    {
      "id": 0,
      "state": "RUNNING",
      "worker_id": "172.18.0.7:8083"
    }
  ],
  "type": "source"
}
```

4. Добавление тестовых данных в PostgreSQL:

```bash
cat ./insert.sql | docker exec -i postgres psql -U debezium -d testdb
```

5. Проверка работы Kafka:

```bash
docker exec -it kafka-1 kafka-topics.sh --bootstrap-server kafka-1:9094 --list
```

6. Запускаем python consumer

```bash
python consumer/kafka_consumer.py
```

7. Проверка метрик Prometheus:

```bash
curl http://localhost:8080/metrics
```
