#!/bin/bash


rm ks.csv
rm kprimes.csv
k=3
n=$k
d=5
gnome-terminal -- bash -c "python server.py $d $n; sleep 30; exit"
gnome-terminal -- bash -c "python agg.py $d $n; sleep 1; exit"&
TERMINAL_PID=$!
sleep 1
for ((j=0;j<n;j++)); do
	g=$RANDOM
	for ((i=0;i<d;i++)); do
		echo -n "$RANDOM," >> ks.csv
		echo -n "$RANDOM," >> kprimes.csv
		python client.py $i $j $g
		sleep 1
	done
	echo "" >> ks.csv
	echo "" >> kprimes.csv
done
sleep 20
