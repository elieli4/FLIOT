
#!/bin/bash

rm bench.csv
rm aggTimes.csv
rm bytesServer.csv
rm bytesAgg.csv
#for i in {1..5}; do
##	for n in {5,10,25,50,100,200,500,1000}; do
##	for d in {3,5,7,11,15,21,25,31,35,41,45,51}; do
#	for m in {1,2,3,4}; do
#		pkill -f agg.py
#        	pkill -f client.py
#		pkill -f server.py
#		echo -n "100,5,$m," >> bench.csv
#		echo -n "100,5,$m," >> aggTimes.csv
#		#./testnoc.sh 100 5 $m
#		./test.sh 100
#		sleep 1
#	        echo "" >> bench.csv
#        	echo "" >> aggTimes.csv
#		sleep 0.1
#	done
#done

#hex=$(openssl rand -hex 18)
#dec=$((0x${hex}))
#echo "$dec"


for i in {1..10}; do
#       for n in {5,10,25,50,100,200,500,1000}; do      
	for d in {5,11,21,31,41,51}; do
        #for m in {1,2,3,4}; do
		pkill -f agg.py
                pkill -f client.py
       	        pkill -f server.py
       	        echo -n "100,$d,3," >> bench.csv
       	        echo -n "100,$d,3," >> aggTimes.csv
       	        ./testnoc.sh 100 $d 3
       	        #./test.sh 100
		sleep 1
       	        echo "" >> bench.csv
       	        echo "" >> aggTimes.csv
       	        sleep 0.1
       	done
done

for i in {1..10}; do
	for n in {5,10,25,50,100,200,500,1000}; do
#       for d in {3,5,7,11,15,21,25,31,35,41,45,51}; do
#        for m in {1,2,3,4}; do
               	pkill -f agg.py
               	pkill -f client.py
               	pkill -f server.py
               	echo -n "$n,5,3," >> bench.csv
               	echo -n "$n,5,3," >> aggTimes.csv
               	./testnoc.sh $n 5 3
               	sleep 1
               	echo "" >> bench.csv
               	echo "" >> aggTimes.csv
               	sleep 0.1
   	done
done

pkill -f agg.py
pkill -f server.py
pkill -f client.py
