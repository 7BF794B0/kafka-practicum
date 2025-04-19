# Система обработки сообщений с блокировкой и цензурой

## Описание
Приложение на Faust (Python) обрабатывает потоковые сообщения из Kafka, осуществляет:
1. **Блокировку**: пользователи могут блокировать/разблокировать других, и сообщения от заблокированных не доставляются.
2. **Цензуру**: слова из динамически обновляемого списка заменяются на `***`.

### Ключевые пояснения:

1. **Модели данных**:
   - `Message`: Основная структура сообщения между пользователями
   - `BlockEvent`: Событие изменения блокировок пользователей
   - `BannedWordEvent`: Событие изменения списка запрещенных слов

2. **Топики Kafka**:
   - `messages`: Входные сообщения от пользователей
   - `blocked_users`: Управление блокировками
   - `banned_words`: Управление запрещенными словами
   - `filtered_messages`: Обработанные сообщения

3. **Таблицы состояний**:
   - `blocked_users_table`: Хранит блоклисты в формате {user: set(blocked_users)}
   - `banned_words_table`: Хранит множество запрещенных слов

4. **Обработчики**:
   - `process_block_events`: Обновляет блоклисты на основе событий
   - `process_banned_words`: Управляет списком запрещенных слов
   - `process_messages`: Основной пайплайн обработки сообщений

5. **Логика цензуры**:
   - `censor_text()` проверяет каждое слово в сообщении
   - Регистронезависимая проверка (приводит слова к нижнему регистру)
   - Заменяет запрещенные слова на `***`

6. **Особенности реализации**:
   - Состояния хранятся на диске через RocksDB
   - Автоматическая обработка конкурирующих обновлений
   - Масштабируемая обработка через партицирование топиков

### Тестирование

1. **Проверка блокировки пользователей:**

   - Отправьте событие блокировки:
     ```bash
     echo 'user1:{"user": "user1", "blocked_user": "user2", "action": "block"}' | docker exec -i kafka-2 kafka-console-producer.sh --broker-list localhost:9095 --topic blocked_users --property parse.key=true --property key.separator=:
     ```

   - Отправьте сообщение от user2 к user1:
     ```bash
     echo ':{"sender": "user2", "recipient": "user1", "text": "Hello!"}' | docker exec -i kafka-2 kafka-console-producer.sh --broker-list localhost:9095 --topic messages --property parse.key=true --property key.separator=:
     ```

   - Убедитесь, что сообщение не появилось в `filtered_messages`.

2. **Проверка цензуры:**

   - Добавьте запрещённое слово:
     ```bash
     echo ':{"word": "spam", "action": "add"}' | docker exec -i kafka-2 kafka-console-producer.sh --broker-list localhost:9095 --topic banned_words --property parse.key=true --property key.separator=:
     ```

   - Отправьте сообщение с запрещённым словом:
     ```bash
     echo ':{"sender": "user3", "recipient": "user4", "text": "Buy spam now!"}' | docker exec -i kafka-2 kafka-console-producer.sh --broker-list localhost:9095 --topic messages --property parse.key=true --property key.separator=:
     ```

   - Проверьте `filtered_messages`:
     ```bash
     docker exec -i kafka-2 kafka-console-consumer.sh --bootstrap-server localhost:9095 --topic filtered_messages --from-beginning
     ```
     Результат: `{"sender": "user3", "recipient": "user4", "text": "Buy *** now!"}`

### Описание логики

- **Блокировка пользователей:** События блокировки хранятся в таблице Faust. При получении сообщения проверяется, находится ли отправитель в чёрном списке получателя.
- **Цензура:** Запрещённые слова хранятся в таблице и динамически обновляются. Все сообщения проходят через фильтр замены запрещённых слов на `***`.
- **Топики Kafka:** Используются для входящих сообщений, фильтрованных сообщений, управления блокировками и запрещёнными словами.

## Запуск проекта
1. Установите Docker и Docker Compose.
2. В корне проекта выполните:
   ```bash
   docker-compose up -d
   ```
3. В данной директории выполнить:
   ```bash
   faust -A app worker -l info
   ```
