# README

Этот проект демонстрирует работу с **Apache Kafka** (в режиме **KRaft**) с использованием **docker-compose**. Пример включает:

1. **Три узла Kafka** (KRaft) и **Kafka UI** для мониторинга.
2. **Приложения на Python**:
   - Продюсер (`producer.py`)
   - Два вида консьюмеров:
     - `single_consumer.py` (читает сообщения по одному, авто-коммит оффсета)
     - `batch_consumer.py` (читает сообщения батчами, ручной коммит оффсета)
3. **Приложения на Go**:
   - Продюсер (`producer.go`)
   - Два вида консьюмеров:
     - `single_consumer.go` (читает сообщения по одному, авто-коммит оффсета)
     - `batch_consumer.go` (читает сообщения батчами, ручной коммит оффсета)
4. **Создание топика** с помощью стандартных утилит Kafka.

## Структура каталогов

```
.
├── README.md
├── docker-compose.yml
├── go
│   ├── batch_consumer.go
│   ├── go.mod
│   ├── go.sum
│   ├── producer.go
│   └── single_consumer.go
├── python
│   ├── batch_consumer.py
│   ├── producer.py
│   └── single_consumer.py
└── topic.txt
```

### Описание ключевых компонентов

- **docker-compose.yml**: поднимает три контейнера Kafka (kafka-1, kafka-2, kafka-3) в режиме KRaft и Kafka UI для визуального управления.
- **go/**: примеры кода на Go
- **python/**: примеры кода на Python
- **topic.txt**: файл с командой для создания топика и результат команды `--describe`.

## 1. Предварительные требования

- **Docker** и **Docker Compose** установлены.
- Для запуска Python-примеров:
  - Установить Python 3.x.
  - Установить пакет `confluent-kafka`:
    ```bash
    pip install confluent-kafka
    ```
- Для запуска Go-примеров:
  - Установить Go (версия 1.18+ или выше).
  - Модуль `github.com/confluentinc/confluent-kafka-go/v2/kafka` прописан в `go.mod`.
    При необходимости выполните в каталоге `go/`:
    ```bash
    go mod tidy
    ```

## 2. Запуск Kafka кластера (KRaft) и Kafka UI

В корневом каталоге проекта есть файл `docker-compose.yml`. Чтобы развернуть кластер запустите:

```bash
docker-compose up -d
```

В результате будут подняты контейнеры:
- **kafka-1**, **kafka-2**, **kafka-3** (три брокера в режиме KRaft)
- **kafka-ui** (доступен по адресу [http://localhost:8080](http://localhost:8080))

Убедитесь, что все контейнеры успешно запустились при помощи команды:

```bash
docker ps
```

## 3. Создание топика

Топик можно создать следующей командой:

```bash
docker exec -it kafka-1 kafka-topics.sh --bootstrap-server localhost:9094 --create --topic my_topic --partitions 3 --replication-factor 2
```

Убедитесь, что топик создан:

```bash
docker exec -it kafka-1 kafka-topics.sh --describe --bootstrap-server localhost:9094 --topic my_topic
```

## 4. Примеры на Python

Все скрипты находятся в каталоге `python/`.

### 4.1. Producer (producer.py)

Отправляет 30 сообщений в топик `my_topic`. Каждое сообщение сериализуется в JSON. Для запуска:

```bash
cd python
python producer.py
```

В консоли вы увидите логи, подтверждающие успешную доставку сообщений.

### 4.2. SingleMessageConsumer (single_consumer.py)

Читает по одному сообщению, выводит результат в консоль, автоматически коммитит оффсет. Запуск:

```bash
python single_consumer.py
```

Чтобы запустить **два** экземпляра (и таким образом «поделить» партиции между ними), можно запустить скрипт в двух разных терминалах или процессах.

### 4.3. BatchMessageConsumer (batch_consumer.py)

Читает сообщения партиями (например, по 10), обрабатывает каждую партию целиком и только после этого один раз коммитит оффсет. Запуск:

```bash
python batch_consumer.py
```

Точно так же можно запустить несколько экземпляров одновременно (партиции будут распределяться между экземплярами внутри одной **consumer group**).

## 5. Примеры на Go

Все скрипты находятся в каталоге `go/`. Перед запуском:

```bash
cd go
go mod tidy  # Установит все необходимые зависимости
```

### 5.1. Producer (producer.go)

Отправляет 30 сообщений в топик `my_topic`. Каждое сообщение сериализуется в JSON. Для запуска:

```bash
go run producer.go
```

### 5.2. SingleMessageConsumer (single_consumer.go)

Читает по одному сообщению, выводит результат в консоль, автоматически коммитит оффсет. Запуск:

```bash
go run single_consumer.go
```

### 5.3. BatchMessageConsumer (batch_consumer.go)

Читает сообщения партиями (например, по 10), обрабатывает каждую партию целиком и только после этого один раз коммитит оффсет. Запуск:

```bash
go run batch_consumer.go
```

## 6. Параллельная работа консьюмеров

- Если вы хотите, чтобы **одни и те же** сообщения обрабатывали *разные приложения* (например, Single и Batch), то используйте **разные `group.id`**. В данном примере это уже сделано: у «single» и «batch» разные group.id.
- Если вы хотите распараллелить обработку **одним** типом консьюмеров, то запускаете несколько экземпляров одного скрипта (или Go-программы) с **одинаковым** `group.id`. Kafka распределит партиции между ними.
