// batch_consumer.go
package main

import (
	"encoding/json"
	"fmt"
	"os"
	"os/signal"
	"sync"
	"syscall"

	"github.com/confluentinc/confluent-kafka-go/v2/kafka"
)

// MyMessage — структура, аналогичная producer.go
type MyMessage struct {
	MsgID int    `json:"msg_id"`
	Text  string `json:"text"`
}

func main() {
	// enable.auto.commit=false, будем коммитить вручную
	consumer, err := kafka.NewConsumer(&kafka.ConfigMap{
		"bootstrap.servers":  "127.0.0.1:9094,127.0.0.1:9095,127.0.0.1:9096",
		"group.id":           "batch-message-consumer-group",
		"auto.offset.reset":  "earliest",
		"enable.auto.commit": false,
	})
	if err != nil {
		panic(err)
	}
	defer consumer.Close()

	err = consumer.SubscribeTopics([]string{"my_topic"}, nil)
	if err != nil {
		panic(err)
	}

	fmt.Println("BatchMessageConsumer started...")

	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)

	run := true

	batchSize := 10
	var batch []*kafka.Message
	batchLock := sync.Mutex{} // на случай, если захотим обрабатывать в нескольких горутинах

	for run {
		select {
		case <-sigChan:
			fmt.Println("BatchMessageConsumer stopped by signal")
			run = false
		default:
			// Ждём сообщение
			msg, err := consumer.ReadMessage(-1)
			if err != nil {
				// Ошибка чтения
				continue
			}
			batchLock.Lock()
			batch = append(batch, msg)
			// Если достигли batchSize, обрабатываем пачку
			if len(batch) >= batchSize {
				processBatch(consumer, batch)
				batch = nil // сбрасываем
			}
			batchLock.Unlock()
		}
	}

	// Перед выходом можно обработать остатки, если они остались
	batchLock.Lock()
	if len(batch) > 0 {
		processBatch(consumer, batch)
	}
	batchLock.Unlock()

	fmt.Println("Closing consumer...")
}

// processBatch — обрабатывает сообщения и делает единоразовый коммит оффсета.
func processBatch(c *kafka.Consumer, batch []*kafka.Message) {
	fmt.Println("[BatchConsumer] Processing batch...")

	for _, m := range batch {
		var data MyMessage
		if err := json.Unmarshal(m.Value, &data); err != nil {
			fmt.Printf("[BatchConsumer] Deserialization error: %v\n", err)
			continue
		}
		fmt.Printf("[BatchConsumer] Handling message: Partition=%d Offset=%d Key=%s Value=%+v\n",
			m.TopicPartition.Partition, m.TopicPartition.Offset, string(m.Key), data)
	}

	// Когда успешно обработали все сообщения из батча, делаем коммит
	_, err := c.Commit() // синхронный (по умолчанию)
	if err != nil {
		fmt.Printf("[BatchConsumer] Commit error: %v\n", err)
	} else {
		fmt.Println("[BatchConsumer] Batch committed.")
	}
}
