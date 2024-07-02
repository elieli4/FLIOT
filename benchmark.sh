
#!/bin/bash

rm bench.csv
rm aggTimes.csv

for n in {5,10,25,50,100,200,500,1000}; do
	pkill -f agg.py
        pkill -f client.py
	pkill -f server.py
	echo -n "$n," >> bench.csv
	echo -n "$n," >> aggTimes.csv
	./test.sh $n
        echo "" >> bench.csv
        echo "" >> aggTimes.csv
	sleep 2
done

pkill -f agg.py
pkill -f server.py
pkill -f client.py
