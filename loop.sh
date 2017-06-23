mv ../../../scripts/a.dat  "../old_packets/a_$(date +%F_%R).dat"
mv ../../../scripts/b.dat  "../old_packets/b_$(date +%F_%R).dat"
mv ../../../scripts/c.dat  "../old_packets/c_$(date +%F_%R).dat"
rm ../logs/*
python3 main.py -f ../../../scripts/a.dat ../../../scripts/b.dat ../../../scripts/c.dat -l -i A B C
