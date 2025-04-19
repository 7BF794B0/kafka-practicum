import faust
from dataclasses import dataclass

# Инициализация Faust приложения
app = faust.App(
    'message-processing-app',                                   # Имя приложения
    broker='127.0.0.1:9094,127.0.0.1:9095,127.0.0.1:9096',      # Адрес Kafka брокера
    store='rocksdb://',                                         # Хранилище состояний на диске
    topic_partitions=3,                                         # Количество партиций в топиках
)

# Модель для представления сообщений между пользователями
@dataclass
class Message(faust.Record):
    sender: str     # Имя отправителя
    recipient: str  # Имя получателя
    text: str       # Текст сообщения

# Модель для событий блокировки/разблокировки
@dataclass
class BlockEvent(faust.Record):
    user: str        # Пользователь, выполняющий действие
    blocked_user: str  # Пользователь, которого блокируют/разблокируют
    action: str      # Тип действия: 'block' или 'unblock'

# Модель для управления запрещенными словами
@dataclass
class BannedWordEvent(faust.Record):
    word: str    # Слово для добавления/удаления
    action: str  # Тип действия: 'add' или 'remove'

# Определение топиков Kafka
messages_topic = app.topic('messages', key_type=str, value_type=Message)
blocked_users_topic = app.topic('blocked_users', key_type=str, value_type=BlockEvent)
banned_words_topic = app.topic('banned_words', key_type=str, value_type=BannedWordEvent)
filtered_messages_topic = app.topic('filtered_messages', key_type=str, value_type=Message)

# Таблицы для хранения состояний
blocked_users_table = app.Table('blocked_users', key_type=str, default=set)
banned_words_table = app.Table('banned_words', key_type=str, default=set)


@app.agent(blocked_users_topic)
async def process_block_events(events):
    """Обработчик событий блокировки/разблокировки пользователей"""
    async for event in events:
        if event.action == 'block':
            # Добавляем пользователя в блоклист
            blocked_users_table[event.user].add(event.blocked_user)
        elif event.action == 'unblock':
            # Удаляем пользователя из блоклиста
            blocked_users_table[event.user].discard(event.blocked_user)

        app.logger.info(f"User {event.user} {event.action}ed {event.blocked_user}")


@app.agent(banned_words_topic)
async def process_banned_words(events):
    """Обработчик управления списком запрещенных слов"""
    async for event in events:
        if event.action == 'add':
            # Добавляем слово в запрещенный список
            banned_words_table['banned_words'].add(event.word)
        elif event.action == 'remove':
            # Удаляем слово из запрещенного списка
            banned_words_table['banned_words'].discard(event.word)

        app.logger.info(f"Word '{event.word}' {event.action}ed")


def censor_text(text: str, banned_words: set) -> str:
    """Функция цензуры: заменяет запрещенные слова на ***"""
    words = text.split()
    return ' '.join(
        '***' if word.lower() in banned_words else word
        for word in words
    )


@app.agent(messages_topic)
async def process_messages(messages):
    """Основной обработчик входящих сообщений"""
    async for msg in messages:
        # Получаем список заблокированных пользователей для получателя
        blocked = blocked_users_table[msg.recipient]

        # Проверяем блокировку отправителя
        if msg.sender in blocked:
            app.logger.info(f"Message from {msg.sender} to {msg.recipient} blocked")
            continue  # Пропускаем заблокированные сообщения

        # Применяем цензуру к тексту
        censored_text = censor_text(msg.text, banned_words_table)

        # Отправляем обработанное сообщение в выходной топик
        await filtered_messages_topic.send(
            value=Message(
                sender=msg.sender,
                recipient=msg.recipient,
                text=censored_text,
            )
        )

if __name__ == '__main__':
    app.main()
    # echo 'user1:{"user": "user1", "blocked_user": "user2", "action": "block"}' | docker exec -i kafka-2 kafka-console-producer.sh --broker-list localhost:9095 --topic blocked_users --property parse.key=true --property key.separator=:
    # echo ':{"sender": "user2", "recipient": "user1", "text": "Hello!"}' | docker exec -i kafka-2 kafka-console-producer.sh --broker-list localhost:9095 --topic messages --property parse.key=true --property key.separator=:
    # echo ':{"word": "spam", "action": "add"}' | docker exec -i kafka-2 kafka-console-producer.sh --broker-list localhost:9095 --topic banned_words --property parse.key=true --property key.separator=:
    # echo ':{"sender": "user3", "recipient": "user4", "text": "Buy spam now!"}' | docker exec -i kafka-2 kafka-console-producer.sh --broker-list localhost:9095 --topic messages --property parse.key=true --property key.separator=:
    # docker exec -i kafka-2 kafka-console-consumer.sh --bootstrap-server localhost:9095 --topic filtered_messages --from-beginning
