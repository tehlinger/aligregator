rm out.txt
echo 'python3 main.py -f data/last_data/MA5.dat data/last_data/MA3.dat data/last_data/MA4.dat -c 0 -i MA4 MA3 MA5'>>out.txt
python3 main.py -f data/last_data/MA5.dat data/last_data/MA3.dat data/last_data/MA4.dat -c 0 -i MA4 MA3 MA5>>out.txt
echo 'python3 main.py -f data/last_data/MA5.dat data/last_data/MA4.dat data/last_data/MA3.dat -c 0 -i MA4 MA3 MA5'>>out.txt
python3 main.py -f data/last_data/MA5.dat data/last_data/MA4.dat data/last_data/MA3.dat -c 0 -i MA4 MA3 MA5>>out.txt
echo 'python3 main.py -f data/last_data/MA4.dat data/last_data/MA5.dat data/last_data/MA3.dat -c 0 -i MA4 MA3 MA5'>>out.txt
python3 main.py -f data/last_data/MA4.dat data/last_data/MA5.dat data/last_data/MA3.dat -c 0 -i MA4 MA3 MA5>>out.txt
echo 'python3 main.py -f data/last_data/MA4.dat data/last_data/MA3.dat data/last_data/MA5.dat -c 0 -i MA4 MA3 MA5'>>out.txt
python3 main.py -f data/last_data/MA4.dat data/last_data/MA3.dat data/last_data/MA5.dat -c 0 -i MA4 MA3 MA5>>out.txt
echo 'python3 main.py -f data/last_data/MA3.dat data/last_data/MA4.dat data/last_data/MA5.dat -c 0 -i MA4 MA3 MA5'>>out.txt
python3 main.py -f data/last_data/MA3.dat data/last_data/MA4.dat data/last_data/MA5.dat -c 0 -i MA4 MA3 MA5>>out.txt
echo 'python3 main.py -f data/last_data/MA3.dat data/last_data/MA5.dat data/last_data/MA4.dat -c 0 -i MA4 MA3 MA5'>>out.txt
python3 main.py -f data/last_data/MA3.dat data/last_data/MA5.dat data/last_data/MA4.dat -c 0 -i MA4 MA3 MA5>>out.txt
clear
cat out.txt | grep 'FLOW\|CHUNK\|E2E\|python'
