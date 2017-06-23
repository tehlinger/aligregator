#!/usr/bin/env python3
import sys
#from pathlib import Path
import pprint
import argparse
import io
from os import listdir
from os.path import isfile, join
from time import time, sleep

from chunks_loader import *
from stats import *
from mcorr_logger import *
from messenger import *
from time_analyzer import *
from aggregator import *
from file_loader import *

#!/usr/bin/env python3
import time
import os
import pprint


logger = init_logger()

def get_parser():
    parser = argparse.ArgumentParser (description='Load chunks of given files')
    parser.add_argument("-f", "--files",dest='files',action="store",nargs='+' )
    parser.add_argument("-c", "--chunks",dest='chunks',action="store",nargs='+')
    parser.add_argument("-i", "--identifiers",dest='ids',action="store",nargs='+')
    parser.add_argument ('-l', '--loop',
            action='store_true',help='continuous mode')
    parser.add_argument ('-s', '--send',
            action='store_true',help='send results')
    return parser

def is_inifinite_mode(args):
    return args.loop

def no_pc_name_has_been_given(args):
    return not hasattr(args,'ids') or not args.ids or len(args.files) != len(args.ids)

def generate_pc_names(args):
    return ["pc"+str(i) for i in range(1,len(args.files)+1)]

def load_stats_once(args):
        r = load_tab(args.files, args.chunks,args.ids)
        tab = sort_packets_ts(r)
        return GlobalStats(tab)

def loop(args):
    try:
        file_not_ok = True
        agg = Aggregator(args.ids)
        tab = None
        file_data = None
        is_running = False
        while file_not_ok:
            try:
                file_data = init_file_data(args)
                agg.update_files_meta(args.files)
            except FileNotFoundError:
                print("File not found")
                sleep(1)
            else:
                file_not_ok = False 
                is_running = True
                print("Loop started.")
        while is_running:
            try:
                tab = load_new_chunks(agg,args)
                if tab:
                    r = GlobalStats(sort_packets_ts(tab))
                    #r = GlobalStats(tab)
                    logger.info("sent N°"+str(r.chunk_id))
                    #print("sent N°"+str(r.chunk_id))
                    #print(r)
                    print(r.to_json())
                    send_msg(r.to_json())
                update_current_chunks(file_data,agg,args)
                sleep (SLEEP_TIME)
            except FileNotFoundError :
                print("File not found")
                sleep(1)
    except (KeyboardInterrupt, SystemExit):
        print("\nApplication interrupted")
        #logger.critical("Application interrupted")

def update_current_chunks(file_data,agg,args):
    change_detected = check_all_files(file_data)
    if change_detected:
        agg.update_files_meta(args.files)

def load_new_chunks(agg,args):
    chunk_id = agg.get_next_chunk_to_load_id()
    if chunk_id != None:
        return load_tab(args.files,[chunk_id],args.ids)


def main():

    args = get_parser().parse_args()
    if no_pc_name_has_been_given(args):
        args.ids = generate_pc_names(args)

    if is_inifinite_mode(args):
        loop(args)
    else:
        result = load_stats_once(args)
        if args.send:
            send_msg(result.to_json())
        else:
            print(result.to_json())

    sys.exit (0)

if __name__ == '__main__':
    main()
