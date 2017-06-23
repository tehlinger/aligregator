#!/usr/bin/env python
import pika
import time


def send_msg(m):
    connection = pika.BlockingConnection(pika.ConnectionParameters('172.16.0.21'))
    channel = connection.channel()
    channel.queue_declare(queue='mode2results',durable=False)
    channel.basic_publish(exchange='',
                          routing_key='tibo',
                          body=m)
    connection.close()
