#mv ../../../scripts/a.dat  "../old_packets/a_$(date +%F_%R).dat"
#mv ../../../scripts/b.dat  "../old_packets/b_$(date +%F_%R).dat"
#mv ../../../scripts/c.dat  "../old_packets/c_$(date +%F_%R).dat"
#rm ../logs/*
#cp ../old_packets/c_2017-06-26_15:49.dat ~/scripts/c.dat
#cp ../old_packets/b_2017-06-26_15:49.dat ~/scripts/b.dat
#cp ../old_packets/a_2017-06-26_15:49.dat ~/scripts/a.dat
python3 main.py -f ../../../scripts/b.dat  ../../../scripts/a.dat ../../../scripts/c.dat -l -i A B C
