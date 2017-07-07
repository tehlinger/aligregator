#!/usr/bin/env python
from subprocess import call
import math
import socket
import struct
import os
import io 
import pika
import pickle
import ctypes as ct
import sys
import random  
import time

#from log import *
#log = init_logger()

LIMIT = 512 
chunk_period = 3

def write_chunk_in_file(lines,f):
    for l in lines:
        f.write(l)

def new_chunk_begins(date_pkt,date_per_file,chunk_period,idPC):
        return date_pkt - date_per_file[idPC] >= chunk_period

def delete_files_if_necessary(chunk_id):
    if chunk_id != 0 and chunk_id % LIMIT == 0:
        os.system("rm *.dat") 

def generate_line(data):
    s_id = data.magic[0]
    idPC = data.magic[n-1]
    date_pkt = (data.magic[n-3]*2**32)/10**9 + data.magic[n-4]/10**9
    bin_ip = data.magic[n-1]
    p_id = (data.magic[n-6]+data.magic[n-5]*2**32+data.magic[n-7])
    f_id = bin_to_int(data.magic[2])+":"+bin_to_int(data.magic[3])
    size = data.magic[n-2]
    return str(s_id)+"|"+ str(f_id)+"|"+ str(p_id)+"|"+ format(date_pkt,'.9f') +"|"+str(size)

def bin_to_int(n):
    return socket.inet_ntoa(struct.pack("<L", n))

def get_file_name(i):
    ip = str(i)
    if ip == "218108076":
        return "a.dat" 
    if ip == "318771372":
        return "b.dat"
    if ip == "335548588":
        return "c.dat"
    print("NO MATCH")

date_per_file = {335548588:0, 318771372:0,218108076:0}
id_per_file =   {335548588:0, 318771372:0,218108076:0}
next_chunks_per_file = {335548588:[], 318771372:[],218108076:[]}

n = 11
chunk_id = 0
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

    line = generate_line(data) 
    idPC = data.magic[n-1]
    date_pkt = (data.magic[n-3]*2**32)/10**9 + data.magic[n-4]/10**9
    lines_list = next_chunks_per_file[idPC]
    lines_list.append(line+"\n")
    f_name = get_file_name(idPC)

    with  open(f_name,"a") as f:
        delete_files_if_necessary(chunk_id)
        if new_chunk_begins(date_pkt,date_per_file,chunk_period,idPC):
            print(str(id_per_file[idPC])+"->" + str(f_name))
            f.write("\t%s|%f|%f\n" % (id_per_file[idPC],date_per_file[idPC],date_pkt))
            write_chunk_in_file(lines_list,f)
            date_per_file[idPC] = date_pkt
            id_per_file[idPC] +=1
            next_chunks_per_file[idPC] = [] 

channel.basic_consume(callback,
                      queue='castTest',
                      no_ack=True)

channel.start_consuming()
