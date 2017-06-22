#!/usr/bin/env python
import pika
import time
import json
import pprint
from subprocess import call
data = ""
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='data', durable=False)
#print(' [*] Waiting for messages. To exit press CTRL+C')

def callback(ch, method, properties, body):
    data = body.decode("utf-8")
    ch.stop_consuming()
    #pprint.pprint(str(data))
    print(data)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback,
                      queue='results',
                      no_ack=True)

channel.start_consuming()
