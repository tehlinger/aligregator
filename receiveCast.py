#!/usr/bin/env python
from subprocess import call
import math
import socket
import struct
import io 
import pika
import pickle
import ctypes as ct
import sys
import random  
import time

from log import *
log = init_logger()

LIMIT = 32 

def bin_to_int(n):
    return socket.inet_ntoa(struct.pack("<L", n))

def open_good_file(i):
    ip = str(i)
    if ip == "218108076":
        return open("a.dat","a") 
    if ip == "318771372":
        return open("b.dat","a") 
    if ip == "335548588":
        return open("c.dat","a") 
    print("NO MATCH")

date_per_file = {335548588:0, 318771372:0,218108076:0}
id_per_file = {335548588:0, 318771372:0,218108076:0}

n = 11
chunk_id = 0
chunk_period = 3
count_pkt = 0

class SkbEvent2(ct.Structure):
     _fields_ = [ ("magic", ct.c_uint32 * n) ]

connection = pika.BlockingConnection(pika.ConnectionParameters(host='172.16.0.21'))
channel = connection.channel()

channel.queue_declare(queue='castTest')

def callback(ch, method, properties, body):
    #print(body)
    data = pickle.loads(body,encoding="bytes")
    global count_pkt
    global chunk_id
    global date_per_file

    s_id = data.magic[0]
    idPC = data.magic[n-1]
    date_pkt = (data.magic[n-4]+data.magic[n-3]*2**32)/10**9
    bin_ip = data.magic[n-1]
    p_id = (data.magic[n-6]+data.magic[n-5]*2**32+data.magic[n-7])
    f_id = bin_to_int(data.magic[2])+":"+bin_to_int(data.magic[3])
    size = data.magic[n-2]

    line =   str(s_id)+"|"+ str(f_id)+"|"+ str(p_id)+"|"+ str(date_pkt)+"|"+str(size)

    #print("%s %f %d" % (data.magic[n-1],date_pkt,data.magic[n-2]))
    #with open("a.dat","a") as a,open("b.dat","a") as b,open("c.dat","a") as c:
    f = open_good_file(idPC)
    #f_name = open_good_file(idPC)
    #f = open(f,"a")
    if chunk_id != 0 and chunk_id % LIMIT == 0:
        os.system("rm *.dat")
    if (date_pkt - date_per_file[idPC] >= chunk_period):
        chunk_id +=1
        print("CHUNK "+str(int(math.floor(chunk_id/3))+" started in file " + ))
        #f.write("\t%s|%f|%f\n" % (id_per_file[idPC],date_per_file[idPC],date_pkt))
        #f.write(line+"\n") 
        #print(line)
        date_per_file[idPC] = date_pkt
        log.info(str(id_per_file[idPC]))
        id_per_file[idPC] +=1
    f.write(line+"\n")
    print(line)
        #if random.randint(0,9)<5:
        #    b.write("%s|%s|%f|%d\n" % (data.magic[0],(data.magic[n-4]+data.magic[n-3]*2**32),date_pkt+1,data.magic[n-2]))
    #datetime.datetime.fromtimestamp(ts)
    #print(str(float(str(data.magic[8])+"."+str(data.magic[7]))))
channel.basic_consume(callback,
                      queue='castTest',
                      no_ack=True)

channel.start_consuming()
