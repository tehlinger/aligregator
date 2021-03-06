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

CHUNK_HISTORIC_SIZE = 3

logger = init_logger()

def loop(args):
    i = 0
    try:
        file_not_ok = True
        agg = Aggregator(args.ids)
        tab = None
        file_data = None
        is_running = True 

        #INFINITE LOOP
        agg = keep_trying_to_load(args,agg)
        file_data = init_file_data(args)
        while is_running:
            try:
                tab = load_new_chunks(agg,args)
                if tab:
#                    print("TAB : \n"+str(tab))
                    i += 1
                    #r = GlobalStats(tab)
                    tmp = sort_packets_ts(tab)
                    r = GlobalStats(tmp)
                    #print("TMP : \n"+str(tmp))
                    #print(r)
                    f = next(iter (r.flows_stats.values()))
                    if i % 2 == 0:
                        i = 0
                        logger.info("C-ID:"+str(r.chunk_id)+"|E2E : "+str(f.e2e.del_stats.avg)+"/s:"+str(f.e2e.loss_stats.s)+"|l:"+str(f.e2e.loss_stats.l))
#                    print("C-ID:"+str(r.chunk_id)+"|E2E : "+str(f.e2e.del_stats.avg)+"/s:"+str(f.e2e.loss_stats.s)+"|l:"+str(f.e2e.loss_stats.l))
                    #print(r.to_json())
                    #print("\n================================\n")
                    #print(r.to_printable_json())
                    send_msg(r.to_json())
                check_files_and_load_new_chunks(file_data,agg,args)
                #sleep (SLEEP_TIME)
            except FileNotFoundError :
                #agg = keep_trying_to_load(args,agg)
                agg = Aggregator(args.ids)
                print("File not found")
                #sleep(1)
            except  KeyboardInterrupt:
                raise
            except Exception as e:
                logger.critical(e)
                print(e)
                time.sleep(0.1)
    except (KeyboardInterrupt, SystemExit):
        print("\nApplication interrupted")
        #logger.critical("Application interrupted")

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
        #print(tab)
        r = GlobalStats(tab)
        return r

def keep_trying_to_load(args,agg):
        file_not_ok = True 
        while file_not_ok:
            try:
                file_data = init_file_data(args)
                agg.update_files_meta(args.files)
            except FileNotFoundError:
                print("File not found")
                sleep(1)
            else:
                file_not_ok = False 
                print("Loop started.")
                logger.critical("Loop started.")
                return agg

def check_files_and_load_new_chunks(file_data,agg,args):
    change_detected = check_all_files(file_data)
    if change_detected:
        agg.update_files_meta(args.files)
    else:
        time.sleep(0.1)

def load_new_chunks(agg,args):
    chunk_id = agg.get_next_chunk_to_load_id()
    ids_list = [chunk_id]
    if chunk_id != None:
        if(int(chunk_id) > CHUNK_HISTORIC_SIZE ):
            for i in range(CHUNK_HISTORIC_SIZE):
                ids_list.append(int(chunk_id)-i)
        return load_tab(args.files,ids_list,args.ids)


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
