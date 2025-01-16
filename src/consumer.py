from kafka import KafkaConsumer
from json import loads
import time

consumer = KafkaConsumer(
    'grav-mig-topic',
    bootstrap_servers=[ <KAFKA-BROKERS> ], 
    auto_offset_reset='earliest', 
    enable_auto_commit=True, # 오프셋 자동 커밋 여부
  #  group_id='test-group', # 컨슈머 그룹 식별자
    key_deserializer=lambda x: loads(x.decode('utf-8')), 
    value_deserializer=lambda x: loads(x.decode('utf-8')),
    consumer_timeout_ms=1000 
)

start = time.time()

for message in consumer:
    print(f'Topic : {message.topic}, Partition : {message.partition}, Offset : {message.offset}, Key : {message.key}, value : {message.value}')
    time.sleep(1)

print('[Done]:', time.time() - start)
