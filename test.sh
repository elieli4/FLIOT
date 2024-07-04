#!/bin/bash


rm ks.csv
rm kprimes.csv
k=$1
n=$k
d=5

for ((i=0;i<d;i++)); do
	for ((j=0;j<n;j++)); do
                r1=$(( RANDOM ))
                r2=$(( RANDOM ))
                echo -n "$r1," >> ks.csv
                echo -n "$r2," >> kprimes.csv
	done
	echo "" >> ks.csv
	echo "" >> kprimes.csv
done

gnome-terminal -- bash -c "python server.py $d $n; sleep 1; exit"
gnome-terminal -- bash -c "python agg.py $d $n; sleep 1; exit"&
TERMINAL_PID=$!
sleep 1
for ((j=0;j<n;j++)); do
	g=$(( RANDOM ))
	for ((i=0;i<d;i++)); do
		python client.py $i $j $g
		#sleep 0.1
	done
done
