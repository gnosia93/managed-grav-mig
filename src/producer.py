from kafka import KafkaProducer
from json import dumps
import time
 
producer = KafkaProducer(
    acks=1,
    compression_type='gzip', 
    bootstrap_servers=['localhost:9092'], 
    key_serializer=lambda x:dumps(x).encode('utf-8'), 
    value_serializer=lambda x:dumps(x).encode('utf-8') 
    
)
 
start = time.time()
 
for i in range(1000000):
    key = 'key-' + str(i)
    value = {'message' : 'whisper .. ' + str(i)}
    producer.send('grav-mig-topic', key=key, value=value)
    producer.flush() # 
    print("key {} value {} published.".format(key, value))
    time.sleep(1)
 
print('[Done]:', time.time() - start)
