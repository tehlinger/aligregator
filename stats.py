#!/usr/bin/env python3
import numpy as np
import pprint
import copy
import json
from collections import OrderedDict

from chunks_loader import *
from stats_calculator import StatsCalculator


class GlobalStats:
    def __init__(self,tab=None):
        if not tab:
            self.bounds = None
            self.flows_stats = {}
        else:
            self.bounds = tab.bounds
            self.chunk_id = tab.chunk_id
            self.calc_flows_stats(tab)

    def to_json(self):
         return json.dumps(dict(self))

    #Iterator used for to_json() method
    def __iter__(self):
        yield('bds',self.bounds)
        yield('id',self.chunk_id)
        for flow_id, stats in self.flows_stats.items():
            yield(str(flow_id),dict(stats))

    def calc_flows_stats(self,tab):
        for flow_id, data in tab.data.items():
            self.fill_flow_stats(flow_id,data,tab.segs)

    def fill_flow_stats(self, flow_id, data,seg_infos):
        if not hasattr(self,'flows_stats'):
            self.flows_stats = {}
        self.flows_stats[flow_id] = FlowStats(data,seg_infos)

    def __str__(self):
     r = ""
     r += str("\n[CHUNK  "+self.chunk_id)
     r += str(" - From "+str(self.bounds[0]) +" To "+str(self.bounds[1]))
     for flow_id, stats in self.flows_stats.items():
         r += "\n\n\t[FLOW "+str(flow_id)+"]\n"+str(stats)
     return r+"]"

class FlowStats(object):
    def __init__(self,data=None,n_seg_infos=None):
        self.segs = []
        self.seg_infos = n_seg_infos
        if data:
            self.e2e = SegStats(data,e2e=True)
            self.segs = []
            if self.seg_infos:
                if self.seg_infos.has_intermediates():
                     for i in range(len(self.seg_infos.seg_ids)):
                        self.segs.append([self.seg_infos.seg_ids[i],SegStats(data,i,i+1)])
            self.set_min_bw()
        else:
            self.e2e = None

    def __str__(self):
        r = ""
        for seg in self.segs:
            r += "\t\t["+seg[0]+"]\n"+str(seg[1])+\
            "\n"
        return "\n\t\t[E2E] :\n "+str(self.e2e)+"\n"+r
        #return "\n[E2E] : "+str(self.e2e)+"\n"+r

    def __eq__(self,other):
        return self.e2e == other.e2e

    def __iter__(self):
        yield("e2e",dict(self.e2e))
        for s in self.segs:
            yield(str(s[0]),dict(s[1]))

    def set_min_bw(self):
        min_bw = None
        for seg_id, seg_stats in self.segs:
            seg_bw = seg_stats.bw_stats
            if seg_bw:
                if min_bw == None or seg_bw.bw < min_bw.bw:
                    min_bw = seg_bw
        self.e2e.bw_stats = copy.deepcopy(min_bw)

class SegStats:
    def __init__(self,flow_data=None,start=-1,stop=-1,seg_infos=None,e2e=False):
        self.is_e2e = e2e
        self.jit_stats = JitterStats()
        self.del_stats = DelayStats()
        self.loss_stats = LossesStats()
        self.bw_stats  = BwStats()
        self.incoherent_stats = False
        if flow_data is not None:
                if type(flow_data) is not str  :
                    self.calc_all_stats(flow_data,start,stop,seg_infos)
                else:
                    self.incoherent_stats = True


    def __str__(self):
            return "\t"+str(self.loss_stats)+"\t"+str(self.del_stats)\
                    +"\t"+str(self.jit_stats)+"\t"+str(self.bw_stats) if not\
                    self.incoherent_stats else "\t\t\tIncoherent flow in this chunk."

    def __iter__(self):
        yield("parent","e2e" if not self.is_e2e else "None")
        yield("j",dict(self.jit_stats))
        yield("d",dict(self.del_stats))
        yield("l",dict(self.loss_stats))
        yield("b",dict(self.bw_stats))

    def calc_all_stats(self,flow_data,start,stop,seg_infos):
        raw_stats = self.all_stats(flow_data,start,stop,seg_infos)
        j = raw_stats["jitters"]
        d = raw_stats["delays"]
        l = raw_stats["losses"]
        b = raw_stats["bw"]
        self.jit_stats.calc(j)
        self.del_stats.calc(d)
        self.loss_stats.calc(l)
        if(self.has_bw(b)):
            self.bw_stats.calc(b)

    def has_bw(self,bw):
        try:
            return bw["total"] is not None and bw["time"] is not None
        except:
            return False

    def all_stats(self,flow_data,start=-1,stop=-1,seg_infos=None):
        analyzer = StatsCalculator(start,stop)

        for p in flow_data.items():
            analyzer.add_packet(p)
	    
        result = analyzer.summary()
        return result

class CommonStats(object):
    def \
    __init__(self,new_avg=None,new_var=None,new_min=None,new_max=None,new_med=None,new_seg_id="E2E"):
        self.avg = new_avg
        self.var = new_var
        self.min = new_min
        self.max = new_max
        self.med = new_med
        self.seg_id = new_seg_id

    def __str__(self):
     return \
             "\t["+\
             " Avg:"+self.pretty_string(self.avg)+" /"+\
             " Var:"+self.pretty_string(self.var)+" /"+\
             " Min:"+self.pretty_string(self.min)+"/"+\
             " Max:"+self.pretty_string(self.max)+"/"+\
             " Med:"+self.pretty_string(self.med)+"]"

    def __iter__(self):
        yield("a",self.avg)
        yield("v",self.var)
        yield("mn",self.min)
        yield("mx",self.max)
        yield("md",self.med)

    def pretty_string(self,data):
        return "<EMPTY DATA>" if data == None else\
            '{:06.10f}'.format(self.avg*1000)+"ms"


    def __eq__(self,other):
        return \
       self.avg == other.avg and\
       self.var == other.var and\
       self.min == other.min and\
       self.max == other.max and\
       self.med == other.med

class JitterStats(CommonStats):
     def __init__(self,new_avg=None,new_var=None,new_min=None,new_max=None,new_med=None):
         super(JitterStats, self).__init__(new_avg,new_var,new_min,new_max,new_med)

     def __str__(self):
         return "\t\tJITTER " +": "+super(JitterStats,self).__str__()

     def __eq__(self,other):
         return \
        self.avg == other.avg and\
        self.var == other.var and\
        self.min == other.min and\
        self.max == other.max and\
        self.med == other.med

     def __iter__(self):
        yield("a",self.avg)
        yield("v",self.var)
        yield("mn",self.min)
        yield("mx",self.max)
        yield("md",self.med)

     def calc(self,jitters):
         array = np.array(jitters["all"])
         self.min = jitters["min"]
         self.max = jitters["max"]
         self.avg = np.average(array)
         self.var = np.var(array)
         self.med = np.median(array)

class BwStats(object):
     def __init__(self,n_total_size=0,n_total_time=1):
         self.total_size=n_total_size
         self.total_time=n_total_time
         self.bw = 0 if (not self.total_time or self.total_time == 0)\
                 else float(self.total_size)/float(self.total_time)

     def __str__(self):
         return "\n\t\t\tBW" +"     : "+self.str_data()

     def __eq__(self,other):
        try:
            if isinstance(other, self.__class__):
                return self.total_size == other.total_size and\
                        self.total_time == other.total_time and\
                        self.bw == other.bw
        except AttributeError:
            print("BW : ATTRIBUTE DIFFER")
            return False
        except:
            raise

     def __iter__(self):
        yield("a",self.bw)

     def str_data(self):
        return \
             "\t["+'{:04.3f}'.format((self.bw/1024.0))+" KB/s"\
             +" / "+str((self.total_size/1024.0))+" KB in "+str(self.total_time)+\
             "sec]"

     def calc(self,bandwidths):
         self.total_size = float(bandwidths["total"])
         self.total_time = float(bandwidths["time"])
         self.bw = 0 if (not self.total_time or self.total_time == 0)\
                 else float(self.total_size)/float(self.total_time)

class DelayStats(CommonStats):

     def __init__(self,new_avg=None,new_var=None,new_min=None,new_max=None,new_med=None):
         super(DelayStats, self).__init__(new_avg,new_var,new_min,new_max,new_med)

     def __str__(self):
         return "\n\t\t\tDELAY  " + ": "+super(DelayStats,self).__str__()+"\n"
         #return " - DELAY  " + ": "+super(DelayStats,self).__str__()+"\n"

     def __eq__(self,other):
         return \
        self.avg == other.avg and\
        self.var == other.var and\
        self.min == other.min and\
        self.max == other.max and\
        self.med == other.med

     def __iter__(self):
        yield("a",self.avg)
        yield("v",self.var)
        yield("mn",self.min)
        yield("mx",self.max)
        yield("md",self.med)

     def calc(self,delays):
         array = np.array(delays["all"])
         self.min = delays["min"]
         self.max = delays["max"]
         self.avg = np.average(array)
         self.var = np.var(array)
         self.med = np.median(array)

class LossesStats(object):
    def \
    __init__(self,new_losses=0,new_successes=0,new_seg_id="E2E"):
        self.l = new_losses
        self.s = new_successes
        if not (self.l == 0 and self.s == 0):
            self.ratio = float(self.s)/float(self.l + self.s)
        else:
            self.ratio = None
        self.seg_id = new_seg_id

    def __str__(self):
        return  "\t\tSUCCES :"\
            +"\t["+'{:02.3f}'.format(self.ratio*100)+"% / "+str(self.s)+" suc./ "\
            +str(self.l)+" loss.]"

    def __eq__(self,other):
        try:
            if isinstance(other, self.__class__):
                return self.l == other.l and\
                        self.s == other.s and\
                        self.ratio == other.ratio
        except AttributeError:
            print("LOSSES : ATTRIBUTE DIFFER")
            return False
        except:
            raise

    def __iter__(self):
       yield("l",self.l)
       yield("s",  self.s)
       yield("r", self.ratio)

    def calc(self,losses):
        self.l = losses["losses"]
        self.s = losses["successes"]
        try:
            self.ratio = float(self.s)/float(self.l + self.s)
        except ZeroDivisionError:
            self.ratio = 0

