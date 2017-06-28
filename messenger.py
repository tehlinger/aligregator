#!/usr/bin/env python
import pika
import time

#QUEUE = 'mode2results' 
QUEUE = 'tibo' 


def send_msg(m):
    connection = pika.BlockingConnection(pika.ConnectionParameters('172.16.0.21'))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE,durable=True)
    channel.basic_publish(exchange='',
                          routing_key=QUEUE,
                          body=m)
    connection.close()
