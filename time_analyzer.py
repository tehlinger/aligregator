#!/usr/bin/env python3
import numpy as np
import pprint
import copy
from collections import OrderedDict

def sort_packets_ts(unsorted_tab):
    swap_instructions = get_swap_instructions(unsorted_tab)
    #print("SWAP : "+str(swap_instructions))
    return apply_swaps(swap_instructions,unsorted_tab)

def apply_swaps(swap_instructions,unsorted_tab):
    for id,instructions in swap_instructions.instructions.items():
        if instructions != None:
            try:
                unsorted_tab.data[id] = apply_swap_to_flow(instructions,unsorted_tab.data[id])
            except ValueError:
                unsorted_tab.data[id]= "Chunk detected incoherent"
    return unsorted_tab

def apply_swap_to_flow(instructions,flow):
    result = OrderedDict()
    for p_id,p in flow.items():
        sorted_p = p.swap(instructions)
        if sorted_p == None:
            #print("No swap instruction")
            return None
        else:
            result[p_id]=sorted_p
    return result

def get_swap_instructions(unsorted_tab):
    result = {}
    for flow_id, packets in unsorted_tab.data.items():
        result[flow_id] = best_guess(packets)
    return SwapInstructions(result)

def best_guess(packets):
    swap_occurences =  count_occurence_for_each_order(packets)
    return most_frequent_order(swap_occurences)

def count_occurence_for_each_order(packets):
    dict_of_occurence_numbers = {}
    stop = False
    for p_id,p in packets.items():
        if p.has_no_loss():
          swaps = p.right_order()
          if swaps != None:
            #stop = True
            if tuple(swaps) in dict_of_occurence_numbers:
                dict_of_occurence_numbers[tuple(swaps)] += 1
            else:
                dict_of_occurence_numbers[tuple(swaps)] = 1
        if stop:
           return dict_of_occurence_numbers
    return dict_of_occurence_numbers

def most_frequent_order(swap_occurences):
    top_candidate = None
    total = -1
    for s, n in swap_occurences.items():
        if n > total:
            total = n
            top_candidate = list(s)
    return top_candidate

class SwapInstructions(object):

    def __init__(self,new_instructions):
        self.instructions = new_instructions

    def __str__(self):
        return pprint.pformat(self.instructions)

    def __eq__(self,other):
        return self.instructions == other.instructions
