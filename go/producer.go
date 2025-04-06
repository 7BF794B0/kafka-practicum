// producer.go
package main

import (
	"encoding/json"
	"fmt"
	"time"

	"github.com/confluentinc/confluent-kafka-go/v2/kafka"
)

// MyMessage — пример структуры, которую будем сериализовать в JSON.
type MyMessage struct {
	MsgID int    `json:"msg_id"`
	Text  string `json:"text"`
}

func main() {
	// Конфиг продюсера. acks=all для «at least once».
	producer, err := kafka.NewProducer(&kafka.ConfigMap{
		"bootstrap.servers": "127.0.0.1:9094,127.0.0.1:9095,127.0.0.1:9096",
		"acks":              "all",
	})
	if err != nil {
		panic(err)
	}
	defer producer.Close()

	// Goroutine для чтения результатов доставки (Delivery Reports).
	go func() {
		for e := range producer.Events() {
			switch ev := e.(type) {
			case *kafka.Message:
				if ev.TopicPartition.Error != nil {
					fmt.Printf("Delivery failed: %v\n", ev.TopicPartition.Error)
				} else {
					fmt.Printf("Message delivered to %v [%d] at offset %v\n",
						*ev.TopicPartition.Topic, ev.TopicPartition.Partition, ev.TopicPartition.Offset)
				}
			}
		}
	}()

	// Отправляем 30 тестовых сообщений
	topic := "my_topic"
	for i := 0; i < 30; i++ {
		// Подготовим объект сообщения
		msgObj := MyMessage{
			MsgID: i,
			Text:  fmt.Sprintf("Hello from Go producer, index=%d", i),
		}

		// Сериализация в JSON
		valBytes, err := json.Marshal(msgObj)
		if err != nil {
			fmt.Printf("[Producer] Error while serializing message: %v\n", err)
			continue
		}

		fmt.Printf("Sending: %+v\n", msgObj)

		// Отправляем в Kafka
		err = producer.Produce(&kafka.Message{
			TopicPartition: kafka.TopicPartition{Topic: &topic, Partition: kafka.PartitionAny},
			Value:          valBytes,
		}, nil)
		if err != nil {
			fmt.Printf("[Producer] Produce error: %v\n", err)
		}

		time.Sleep(1 * time.Second)
	}

	// Ждём подтверждения отправки всех сообщений (макс. 15 секунд)
	producer.Flush(15 * 1000)

	fmt.Println("Producer finished sending messages.")
}
