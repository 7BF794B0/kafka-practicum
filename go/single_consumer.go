// single_consumer.go
package main

import (
	"encoding/json"
	"fmt"
	"os"
	"os/signal"
	"syscall"

	"github.com/confluentinc/confluent-kafka-go/v2/kafka"
)

// MyMessage — структура, аналогичная producer.go
type MyMessage struct {
	MsgID int    `json:"msg_id"`
	Text  string `json:"text"`
}

func main() {
	// Конфигурация: auto.commit включён
	consumer, err := kafka.NewConsumer(&kafka.ConfigMap{
		"bootstrap.servers":  "127.0.0.1:9094,127.0.0.1:9095,127.0.0.1:9096",
		"group.id":           "single-message-consumer-group",
		"auto.offset.reset":  "earliest",
		"enable.auto.commit": true,
	})
	if err != nil {
		panic(err)
	}
	defer consumer.Close()

	// Подписка на топик
	err = consumer.SubscribeTopics([]string{"my_topic"}, nil)
	if err != nil {
		panic(err)
	}

	fmt.Println("SingleMessageConsumer started...")

	// Ловим Ctrl+C, чтобы корректно завершаться
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)

	run := true
	for run {
		select {
		case <-sigChan:
			fmt.Println("SingleMessageConsumer stopped by signal")
			run = false
		default:
			// Пытаемся считать сообщение (1 сек таймаут)
			msg, err := consumer.ReadMessage(-1)
			if err != nil {
				// Если ошибка (например, таймаут), просто пропускаем
				// ReadMessage(timeout) выбросит ошибку, если timeout != -1
				// Если timeout = -1, ждём бесконечно, пока появится сообщение
				continue
			}

			// Десериализация
			var data MyMessage
			err = json.Unmarshal(msg.Value, &data)
			if err != nil {
				fmt.Printf("[SingleConsumer] Deserialization error: %v\n", err)
				continue
			}

			// Обработка
			fmt.Printf("[SingleConsumer] Received message: Partition=%d Offset=%d Key=%s Value=%+v\n",
				msg.TopicPartition.Partition, msg.TopicPartition.Offset, string(msg.Key), data)
		}
	}

	fmt.Println("Closing consumer...")
}
