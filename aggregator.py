#!/usr/bin/env python3
import numpy as np
import pprint
import copy
from collections import OrderedDict

from chunks_loader import *

class Action:
        IDLE, DEL, LOAD = range(3)

class Aggregator(object):

    def __init__(self,ids=""):
        self.last_chunk_is_complete = False
        self.must_delete_last_chunk=False
        self.metadata=ChunksMetadata(len(ids))

    def get_next_chunk_to_load_id(self):
        for l in self.metadata.lines:
            if l.is_complete():
                r = l.index
                self.metadata.delete(l)
                return r
        return None

    def update_files_meta(self,files):
        i = 0
        for f in files :
            found_chunks = load_all_chunk_metadatas(f)
            for c in found_chunks:
                self.metadata.set_true(int(c.id),i)
            i += 1

    def __eq__(self,other):
        return self.metadata == other.metadata

    def __str__(self):
        return "[Must delete line : "+ str(self.last_chunk_is_complete)\
                +"\nLast chunk is complete : "+str(self.last_chunk_is_complete)+\
                "\nMetadata :\n"+str(self.metadata)

    def add(self,line,col):
        return self.metadata.set_true(line,col)


    def has_nothing_to_do(self):
        return not self.last_chunk_is_complete and not\
    self.must_delete_last_chunk



class ChunksMetadata(object):

    def __init__(self,n_ids,n_lines=1):
        self.n_col = n_ids
        self.width = n_ids
        self.lines = []
        for i in range(n_lines):
            self.lines.append(Line(i,self.width))

    def __eq__(self,other):
        return self.width == other.width and\
                self.lines == other.lines

    def __str__(self):
        return "N cols : "+str(self.n_col)+"\nWidth : "+str(self.width)+\
                "\nLines :\n"+self.str_lines()

    def set_true(self,line,col):
        if col < self.width:
            for l in self.lines:
                if l.index == line:
                    l.set_true_at(col)
                    if l.is_complete():
                        return Action.LOAD
                    else:
                        return Action.IDLE
            new_line = Line(len(self.lines),self.width)
            new_line.set_true_at(col)
            self.lines.append(new_line)
            return Action.IDLE
        else:
            raise ValueError('Could not add element : width smaller than '+str(col))

    def add_line(self):
        new_line = Line(len(self.lines),self.width)
        new_line.set_true_at(col)
        self.lines.append(new_line)

    def delete(self,l):
        self.lines.remove(l)

    def str_lines(self):
        r = ""
        for l in self.lines:
            r +=str(l)+"\n"
        return r

    def has_same_lines_than(self,other):
        for i in len(self.lines):
            self_line = self.lines[i]
            other_line = other.lines[i]
            if(self_line != other_line):
                return False
        return True


    def has(self,chunk_index,col):
        if col < self.width:
            for line in self.lines:
                if line.index == chunk_index:
                    return line.values[col]
            return False
        else:
            raise ValueError('Chunk metadata width smaller than '+str(col))


class Line:

    def __init__(self,new_chunk_index, n_width):
        self.index = new_chunk_index
        self.values   = [False for i in range(n_width)]
        self.already_loaded =  False

    def __eq__(self,other):
        return self.index == other.index and\
                self.values == other.values

    def __str__(self):
        return "["+str(self.index)+" : "+str(self.values) +" ]"

    def set_true_at(self,i):
        if i < len(self.values):
            self.values[i] = True
        else:
            raise ValueError('Could not add element : width smaller than '\
                    +str(i))

    def is_complete(self):
        for state in self.values:
            if not state:
                return False
        return True
