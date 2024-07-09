
#!/bin/bash

rm bench.csv
rm aggTimes.csv

for i in {1..5}; do
	for n in {5,10,25,50,100,200,500,1000}; do
#	for n in {1000,2000}; do
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
