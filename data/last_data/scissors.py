#!/usr/bin/env python3
import sys
from pathlib import Path
import pprint
import argparse
import io
from os import listdir
from os.path import isfile, join

def extract_file(path):
    if '/' in path:
        return path.split('/')[-1]
    else:
        return path

def is_new_chunk(ts,current_limit):
    return not current_limit or ts > current_limit

def extract_target_files(arg):
    if not arg:
        onlyfiles = [f for f in listdir('.') if isfile(join('.', f))]
        return [f for f in onlyfiles if "dat" in f and not "cut" in f] 
    else:
        return arg

def generate_chunked_file(f,new_file_name,chunk_size):
    first_read = True
    current_start = None
    current_limit = None
    chunk_num = 0
    with open(f,"r") as text, open(new_file_name,"w") as output:
        for line in text.readlines():
            p_data = line.rstrip().split('|')
            p_ts = float(p_data[-2])
            if is_new_chunk(p_ts,current_limit):
                current_start = p_ts
                current_limit = p_ts + chunk_size
                output.write('\t'+str(chunk_num)+'|'+str(current_start)+'|'+str(current_limit)+'\n')
                chunk_num += 1
            output.write(line)


def create_chunks(files_list,chunk_size=5):
    for path in files_list:
        f = extract_file(path)
        new_file_name = 'cut_'+f
        generate_chunked_file(path,new_file_name,chunk_size)

##############################################################################
# Main
##############################################################################

def main():
    global verbose
    #
    # Argument parsing
    #
    
    DEF_CHUNK_SIZE = 3

    parser = argparse.ArgumentParser (description='Capture file scissors')
    parser.add_argument("-f", "--file",dest='file',action="store",nargs=1 )
    parser.add_argument("-t", "--time",dest='size',action="store",nargs=1 )
    args = parser.parse_args ()
    files_list = extract_target_files(args.file)
    chunk_size = int(args.size[0]) if (args.size) else DEF_CHUNK_SIZE
    create_chunks(files_list,chunk_size) 

    sys.exit (0)

if __name__ == '__main__':
    main()
