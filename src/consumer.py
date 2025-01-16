from kafka import KafkaConsumer
from json import loads

consumer = KafkaConsumer(
    'topic2',
    bootstrap_servers=[ <KAFKA-BROKERS> ], 
    auto_offset_reset='earliest', 
    enable_auto_commit=True, # 오프셋 자동 커밋 여부
  #  group_id='test-group', # 컨슈머 그룹 식별자
    key_deserializer=lambda x: loads(x.decode('utf-8')), 
    value_deserializer=lambda x: loads(x.decode('utf-8')),
    consumer_timeout_ms=1000 
)

print('[Start] get consumer')

for message in consumer:
    print(f'Topic : {message.topic}, Partition : {message.partition}, Offset : {message.offset}, Key : {message.key}, value : {message.value}')

print('[End] get consumer')
