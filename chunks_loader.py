#!/usr/bin/env python3
import pprint
import copy
from collections import OrderedDict

from time_analyzer import *

class Chunk_position:
        FIRST, LAST, INTERMEDIATE = range(3)

def load_tab(f_names,chunk_ids,agent_ids=None):
        tab = init_tab(chunk_ids,f_names,agent_ids)
        tab = load_chunks(tab,f_names[1],chunk_ids,Chunk_position.LAST)
        for f in f_names[2:]:
                tab = load_chunks(tab,f,chunk_ids,Chunk_position.INTERMEDIATE)
        return tab

def init_tab(chunk_ids,f_names,agent_ids):
    if len(f_names) < 2:
        raise NameError('Need at least two files')
    if len(chunk_ids) < 1:
        raise NameError('Need at least one chunk id')
    result = Tab(load_chunk(chunk_ids[0],f_names[0]),Chunk_position.FIRST,agent_ids)
    return result

def load_chunks(tab,f_name,chunk_ids,position):
    for i in chunk_ids:
        chunk = load_chunk(i,f_name)
        tab.add_chunk(chunk,position)
        #if chunk != None:
        #    tab.add_chunk(chunk,position)
    return tab

def load_chunk(chunk_id,filename):
    with open(filename,"r") as f:
        for line in f:
            if is_valid(line):
                if is_header(line):
                    chunk = Chunk()
                    chunk.fill_metadata(line)
                    if(chunk.matches(chunk_id)):
                           chunk.fill_data(f)
                           return chunk

def load_all_chunk_metadatas(filename):
    with open(filename,"r") as f:
        result = []
        for line in f:
            if is_valid(line):
                if is_header(line):
                    chunk_meta = Chunk()
                    chunk_meta.fill_metadata(line)
                    result.append(chunk_meta)
        return result


def is_valid(line):
    l = line.split('|')
    if len(l) < 3:
        return False
    try:
        x = float(l[2])
    except ValueError as e:
        try:
            x = float(l[3])
            return len(l) >= 3 and l[1] and l[2]
        except:
            pass
        #If the timestamp field of the string is not a float, then
        #the line is invalis
        return False
    return len(l) >= 3 and l[1] and l[2]

def is_header(line):
    return "\t" in line

class Chunk:
    def __init__(self,new_id=None,new_bound=None,new_data=None):
        self.data = new_data or OrderedDict()
        self.id = new_id
        self.bounds = new_bound or [-1,-1]

    def __str__(self):
        return "ID:"+self.id+"\nBounds"+str(self.bounds)+"\nPackets:" +\
                str(self.data)

    def matches(self,num):
        return str(num) == str(self.id)

    def fill_metadata(self,line):
        if is_valid(line):
            if is_header(line) :
                elements = line.split("|")
                result = {}
                self.id  = elements[0].replace("\t","")
                self.bounds = [float(elements[1]),float(elements[2])]
            else:
                   raise NameError('Unkown line format :'+line)

    def fill_data(self,f):
        for line in f:
            if is_valid(line):
                if is_header(line):
                    break
                else:
                    elements = line.rstrip().split("|")
                    has_f_id = len(elements) == 5
                    s_id = elements[0]
                    if not has_f_id:
                        p_id = elements[1]
                        ts = float(elements[2])
                        p_size = None if len(elements) < 4 else int(elements[3])
                        if s_id not in self.data:
                            self.data[s_id] = OrderedDict()
                        if not p_size:
                            self.data[s_id][p_id] = ts
                        else:
                            self.data[s_id][p_id] = [ts,p_size]
                    else:
                        self.has_f_id = True
                        f_id = str(elements[1])
                        p_id = elements[2]
                        ts = float(elements[3])
                        p_size =  int(elements[4])
                        s_id = s_id+"|"+f_id
                        if s_id not in self.data:
                            self.data[s_id] = OrderedDict()
                        if not p_size:
                            self.data[s_id][p_id] = ts
                        else:
                            self.data[s_id][p_id] = [ts,p_size]


class Tab:
    def\
    __init__(self,chunk=None,chunk_position=Chunk_position.FIRST,new_agent_ids=None):
        if not chunk:
            self.data = {}
        else:
            if not hasattr(self,'data'):
                self.data = {}
            if hasattr(chunk,'has_f_id'):
                self.has_f_id = True
            else:
                if not hasattr(self,'has_flows'):
                    self.has_f_id = False
            self.chunk_id = chunk.id if chunk.id else None
            self.bounds = None
            self.add_first_chunk(chunk,chunk_position)
            self.add_bounds(chunk)
        self.segs = Seg_manager(new_agent_ids)

    def __eq__(self, other):
        for flow_id, packets in self.data.items():
            flow = self.data[flow_id]
            if flow_id not in other.data:
                return False
            else:
                for p_id, ts in flow.items():
                    if p_id not in other.data[flow_id]:
                        return False
                    else:
                        if ts != other.data[flow_id][p_id]:
                            return False
        return True

    def has_flows(self):
        if hasattr(self,'has_f_id'):
            return self.has_f_id
        else:
            return False

    def size(self):
	    return len(self.data)

    def __str__(self):
        if hasattr(self,'data'):
            r = ""
            if hasattr(self,'bounds'):
                r +="["+str(self.bounds[0])+";"+str(self.bounds[1])+"]\n"
            if self.has_flows():
                r +="HAS FLOWS\n"
            if hasattr(self,'chunk_id'):
                r +="[Chunk ID : "+self.chunk_id+"]\n"
            r+="\nSegments:"+str(self.segs)+"\n"
            for flow_id,packets in self.data.items():
                r += (str(flow_id) + "\n")
                if packets != None:
                    for p_id,ts in packets.items():
                        r += ("\t"+str(p_id) +" "+ str(ts)+"\n")
            return r

    def __eq__(self, other):
        """Override the default Equals behavior"""
        try:
            if isinstance(other, self.__class__):
                return self.data == other.data and\
                        self.bounds == other.bounds and\
                        self.chunk_id == other.chunk_id
        except AttributeError:
            return False
        except:
            raise

    def set_data(self,new_data):
        self.data = new_data

    def add_bounds(self,chunk):
        if not hasattr(self,'bounds') or (self.bounds == None\
                or len(self.bounds) <2):
            self.bounds = chunk.bounds
        else:
            self.bounds[0] = min(chunk.bounds[0],self.bounds[0])
            self.bounds[1] = max(chunk.bounds[1],self.bounds[1])

    def add_first_chunk(self,chunk,chunk_position):
        for flow_id, packets in chunk.data.items():
                self.add_new_flow(flow_id,packets,chunk_position)

    def add_chunk(self,chunk,chunk_position):
        self.add_bounds(chunk)
        for flow_id, packets in chunk.data.items():
            if self.has_flow(flow_id):
                self.merge_flows(flow_id,packets,chunk_position)

    def has_flow(self,flow_id):
            return flow_id in self.data.keys()

    def add_new_flow(self,flow_id,packets,chunk_position):
        self.data[flow_id] = OrderedDict()
        if self.has_flows():
            line = flow_id.split("|")
            f_id = line[0]
            s_id = line[1]
            self.data[flow_id]["s_id"]=s_id
            self.data[flow_id]["f_id"]=f_id
        for p_id, ts in packets.items():
            self.data[flow_id][p_id] = new_ts(ts)

    def merge_flows(self,flow_id,packets,chunk_position):
        flow =self.data[flow_id]
        if self.has_flows():
            line = flow_id.split("|")
            f_id = line[0]
            s_id = line[1]
            self.data[flow_id]["s_id"]=s_id
            self.data[flow_id]["f_id"]=f_id
        for p_id, ts in packets.items():
            add_ts(flow,p_id,ts,chunk_position)

    def has_intermediates(self):
        return self.segs.has_intermediates()

def new_ts(ts):
    result = Packet()
    #ts is a list if sizes are present in file, integer otherwise
    if type(ts) is not list:
        result.first = float(ts)
    else:
        result.first = ts[0]
        result.size = ts[1]
    return result

def add_ts(flow_dict, p_id,ts,chunk_position):
    if p_id in flow_dict:
        t = flow_dict[p_id]
        t.add_ts(ts,chunk_position)
        flow_dict[p_id] = t

class Packet:
    def __init__(self,new_first=None,new_last=None,new_inter=None,new_p_size=None):
        self.first = new_first
        self.last = new_last
        self.inter = new_inter if new_inter else []
        self.size = new_p_size

    def __eq__(self, other):
        try:
            size_ok = (not hasattr(self,'size') and not hasattr(other,'size'))\
                    or self.size == other.size
            return size_ok and \
                    self.first == other.first and \
                    self.last == other.last and \
                    self.inter == other.inter
        except AttributeError:
            return False
        except:
            raise

    def __str__(self):
        size_str = "" if not hasattr(self,'size') or not self.size \
                else str(self.size)+" bytes"
        return "{["+str(self.first)+" , "+str(self.last)+" , "\
                +str(self.inter)+"];"+size_str+"}"

    def add_ts(self,ts,position):
        if type(ts) is not list:
            time = ts
        else:
            time = ts[0]
        if position == Chunk_position.FIRST:
            self.first = float(time)
        elif position == Chunk_position.LAST:
            self.last = float(time)
        elif position == Chunk_position.INTERMEDIATE:
            if self.inter:
                self.inter.append(float(time))
            else:
                self.inter = [float(time)]

    def delay_between(self,start=-1,stop=-1):
        if self.is_end_to_end(start,stop):
            if not self.first or not self.last:
                #raise NameError('Packet missing a timestamp : \n'+str(self))
                return None
            else:
                result = float(self.last) - float(self.first)
                return result
        else:
            return self.exact_delay_between(start,stop)

    def right_order(self):
        l = self.get_ts_as_list()
        #thanks stackoverflow :
        #https://stackoverflow.com/questions/6422700/how-to-get-indices-of-a-sorted-array-in-python
        r = [i[0] for i in sorted(enumerate(l), key=lambda x:x[1])]
        return r

    def get_ts_as_list(self):
        r = []
        r.append(self.first)
        for ts in self.inter:
            r.append(ts)
        r.append(self.last)
        return r

    def swap(self,instructions):
        try:
            if(self.instructions_has_good_length(instructions)):
                f =  self.swap_index(instructions[0])
                target = []
                for i in instructions[1:-1]:
                    target.append(self.swap_index(i))
                l =  self.swap_index(instructions[-1])
                result = Packet(f,l,target,self.size)
                if strictly_increasing(result.get_ts_as_list()):
                    return result
                else :
	    	#BUG : does currently not swap FIRST and LAST time
                    #print("Not increasing : "+str(result))
                    return result 
            else:
                    raise ValueError(str(instructions)+' instructions'\
                            +' do not apply with '+str(self))
        except:
            return self

    def swap_index(self,i):
        if i == 0:
            return self.first
        elif (self.inter == None and i == 1)\
                or (i == (len(self.inter)+1)):
            return self.last
        else:
            return self.inter[i - 1]

    def instructions_has_good_length(self,i):
        if i == None:
            return False
        if self.inter == None :
            return len(i) == 2
        else :
            return (len(i) == len(self.inter)+2)


    def has_no_loss(self):
        return not self.has_loss_between(-1,-1)

    def has_loss_between(self,start=None,stop=None):
        if self.is_end_to_end(start,stop):
            return not self.last
        else:
            return self.time_at(stop) == None

    def was_exactly_lost_between(self,start,stop):
        if stop == -1 and start == -1:
            return True
        else:
            valid_start = self.time_at(start) != None
            valid_stop = self.time_at(stop) != None
            return valid_start != valid_stop

    def start_at(self,start):
        if start == -1:
            return self.first
        else:
            return self.time_at(start)

    def has_reached(self,start):
        result = self.time_at(start) != None
        return result

    def exact_delay_between(self,start,stop):
        beg = self.first if start == -1 else self.time_at(start)
        end = self.last if stop == -1 else self.time_at(stop)
        if end and beg:
            return end - beg

    def time_at(self,index):
        num_jumps = len(self.inter)+1
        if index == (len(self.inter)+1):
            return  self.last
        elif index == 0:
            return  self.first
        else:
            if(len(self.inter) < index-1):
                return None
            else:
                return  self.inter[index - 1]

    def is_end_to_end(self,start,stop):
        return start == -1 and stop == -1

    def has_size(self):
        return hasattr(self,'size') and self.size

class Seg_manager:

    def __init__(self,new_agent_ids):
        self.agent_ids = new_agent_ids
        self.num_segs = 0 if not new_agent_ids else len(new_agent_ids)-1
        self.seg_ids = []
        if self.has_intermediates():
            for i in range(len(self.agent_ids)-1):
                self.seg_ids.append(self.get_id(i,i+1))

    def __str__(self):
        return self.get_all_segs()

    def e2e_lbl(self):
	    return str(self.agent_ids[0])+":"+str(self.agent_ids[-1])

    def has_intermediates(self):
        return self.num_segs > 0

    def get_id(self,i,j):
        if i < len(self.agent_ids) and j < len(self.agent_ids):
            return str(self.agent_ids[i])+":"+str(self.agent_ids[j])
        else:
            return "No_match:"+str(i)+"-"+str(j)

    def get_all_segs(self):
        r = "["
        if hasattr(self,'agent_ids') and self.agent_ids:
            for i in range(len(self.agent_ids)-1):
                r += self.get_id(i,i+1)+";"
        return r + "]"
#Thanks stackoverflow:
#https://stackoverflow.com/questions/4983258/python-how-to-check-list-monotonicity
def strictly_increasing(L):
    l = [x for x in L if x != None]
    return all(x<y for x, y in zip(l, l[1:]))
