rm result.txt ;clear;python3 ../main.py -f ../data/last_data/MA3.dat ../data/last_data/MA5.dat ../data/last_data/MA4.dat  -c 0 -i MA4 MA3 MA5 > result.txt; cat result.txt | python3 -m json.tool
