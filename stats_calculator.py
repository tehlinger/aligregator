#!/usr/bin/env python3
import numpy as np
import pprint
import copy
from collections import OrderedDict

from chunks_loader import *

class StatsCalculator(object):

    def __init__(self,new_start,new_stop):
         self.start = new_start
         self.stop = new_stop
         self.last_delay= self.new_delay  = None
         self.t_min = self.t_max = self.d_min = self.d_max = self.j_min = self.j_max = None
         self.delays = []
         self.jitters =[]
         self.bws = []
         self.losses = self.total = self.total_bytes= 0
         self.stats_are_for_e2e = self.is_e2e(self.start,self.stop)
         self.invalid_chunk = False


    def add_packet(self,p):
        packet = p[1]
        if self.stats_are_for_e2e or packet.has_reached(self.start):
            self.total += 1
        if packet.has_loss_between(self.start,self.stop):
            if  self.stats_are_for_e2e or \
                    packet.was_exactly_lost_between(self.start,self.stop):
                    self.losses +=1
            self.last_delay = None
        else:
            t = packet.start_at(self.start)
            if t is not None:
                self.t_min = self.min_val(t,self.t_min)
                self.t_max = self.max_val(t,self.t_max)
            new_delay = packet.delay_between(self.start,self.stop)
            if new_delay != None:
                self.d_max   = self.max_val(new_delay,self.d_max)
                self.d_min   = self.min_val(new_delay,self.d_min)
                self.delays.append(new_delay)
                if packet.has_size():
                    self.total_bytes += packet.size
                if self.last_packet_was_ok():
                    new_jit = new_delay - self.last_delay
                    self.j_min   = self.min_val(new_jit,self.j_min)
                    self.j_max   = self.max_val(new_jit,self.j_max)
                    self.jitters.append(new_jit)
                self.last_delay = new_delay

    #def add_packet(self,p):
    #    packet = p[1]
    #    if self.stats_are_for_e2e or packet.has_reached(self.start):
    #        self.total += 1
    #    if packet.has_loss_between(self.start,self.stop):
    #        if  self.stats_are_for_e2e or \
    #                packet.was_exactly_lost_between(self.start,self.stop):
    #                self.losses +=1
    #        self.last_delay = None
    #    else:
    #        try:
    #            t = packet.start_at(self.start)
    #            if t is not None:
    #                self.t_min = self.min_val(t,self.t_min)
    #                self.t_max = self.max_val(t,self.t_max)
    #            new_delay = packet.delay_between(self.start,self.stop)
    #            if new_delay != None:
    #                self.d_max   = self.max_val(new_delay,self.d_max)
    #                self.d_min   = self.min_val(new_delay,self.d_min)
    #                self.delays.append(new_delay)
    #                if packet.has_size():
    #                    self.total_bytes += packet.size
    #            if self.last_packet_was_ok():
    #                new_jit = new_delay - self.last_delay
    #                self.j_min   = self.min_val(new_jit,self.j_min)
    #                self.j_max   = self.max_val(new_jit,self.j_max)
    #                self.jitters.append(new_jit)
    #            self.last_delay = new_delay
    #        except NameError:
    #            return


    def summary(self):
        if self.invalid_chunk:
            print("Invalid chunk : \n"+str(self))
            return self.empty_data()
        try:
            bw = None if self.stats_are_for_e2e else \
                    {"total":self.total_bytes,"time":(self.t_max - self.t_min)}
            return \
                {"total" : self.total, "losses":self.losses,\
                "delays":{"all":self.delays,"min":self.d_min,"max":self.d_max},\
                "jitters":{"all":self.jitters,"min":self.j_min,"max":self.j_max},\
                "losses":{"losses":self.losses,"successes":(self.total-self.losses)},\
                "bw":bw}
        #Case where the chunk is empty
        except TypeError:
            return \
                {"total" : self.total, "losses":self.losses,\
                "delays":{"all":self.delays,"min":self.d_min,"max":self.d_max},\
                "jitters":{"all":self.jitters,"min":self.j_min,"max":self.j_max},\
                "losses":{"losses":self.losses,"successes":(self.total-self.losses)},\
                "bw":None}

    def empty_data(self):
        return \
                {"total" : self.total, "losses":self.losses,\
                "delays":{"all":self.delays,"min":self.d_min,"max":self.d_max},\
                "jitters":{"all":self.jitters,"min":self.j_min,"max":self.j_max},\
                "losses":{"losses":self.losses,"successes":(self.total-self.losses)},\
                "bw":None}


    def is_e2e(self,start,stop):
        return start == -1 and stop == -1

    def last_packet_was_ok(self):
        return self.last_delay is not None

    def min_val(self,new_val,v_min):
        if not v_min:
            return new_val
        else:
            return min(new_val,v_min)

    def max_val(self,new_val,v_max):
        if not v_max:
            return new_val
        else:
            return max(new_val,v_max)
