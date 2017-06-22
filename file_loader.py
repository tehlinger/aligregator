#!/usr/bin/env python3
import time
import os
import pprint

SLEEP_TIME=0.1

def check_all_files(file_data):
    result = False
    for name, size in file_data.items():
        update = has_file_changed(name,size)
        has_changed = update[0]
        if has_changed:
            file_data[name] = update[1]
            result = True
    return result

def init_file_data(args):
    result = {}
    for f in args.files:
        result[f] = -1
    return result

def file_modified(prev_size,filename):
    new_size = os.stat(filename).st_size
    return prev_size == -1 or prev_size != new_size

def check_file(filename):
        last_line = -1
        keep_going = True
        file_size = -1
        try:
            if file_modified(file_size,filename):
                file_size = os.stat(filename).st_size
                fp = open(filename)
                for i, line in enumerate(fp):
                    if i > last_line:
                        print(line.strip("\n"))
                        last_line += 1
            time.sleep(SLEEP_TIME)
        except (KeyboardInterrupt, SystemExit):
            raise
        except FileNotFoundError:
            pass


def has_file_changed(filename,prev_size):
        last_line = -1
        keep_going = True
        file_size = -1
        try:
            if file_modified(prev_size,filename):
                return [True,os.stat(filename).st_size]
            else:
                return [False,None]
        except FileNotFoundError:
            pass

#if __name__ == '__main__':
#    check_file("data/random.txt")
