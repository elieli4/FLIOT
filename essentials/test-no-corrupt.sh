#!/bin/bash


rm ks.csv
rm kprimes.csv
rm inputs.csv
rm checksums.csv

pkill -f agg.py
pkill -f client.py
pkill -f server.py

if [ "$#" -lt 2 ]; then
	echo "Usage: ./test-no-corrupt.sh <n> <d>"
	exit 1
fi
k=$1
n=$k
d=$2
byte=3
l=$((2 **($byte*8)))
m=$(($l -1))
echo "d: $d, n: $n"
if [ "$d" -lt 3 ]; then
	echo "IMPORTANT: d must be at least 3. Restart"
	exit 1
fi
sum=0

echo ""
echo "Printing the correct input value for each group"

for ((j=0;j<n;j++)); do
	g=$(shuf -i 0-$m -n 1)
	echo "$g"
	sum=$((sum + g))
	for ((i=0;i<d;i++)); do
		hex=$(openssl rand -hex 18)
		r1=$((0x${hex}))
		if [ "$r1" -lt 0 ]; then
			r1=$((r1 * -1))
		fi
                hex1=$(openssl rand -hex 18)
                r2=$((0x${hex1}))
		if [ "$r2" -lt 0 ]; then
                        r2=$((r1 * -1))
                fi
		v=$(( g + r1 ))
		c=$(( g + r2 ))
		if [ $i -eq $((d-1)) ]; then
			echo -n "$v" >> inputs.csv
			echo -n "$c" >> checksums.csv
			echo -n "$r1" >> ks.csv
      			echo -n "$r2" >> kprimes.csv
			break
		fi
		echo -n "$r1," >> ks.csv
    		echo -n "$r2," >> kprimes.csv
		echo -n "$v," >> inputs.csv
		echo -n "$c," >> checksums.csv
		#python client.py $i $j $g
		#sleep 0.1
	done
	echo "" >> ks.csv
  	echo "" >> kprimes.csv
	echo "" >> inputs.csv
	echo "" >> checksums.csv
done

echo ""

sleep 1
gnome-terminal --title="Server" -- bash -c "python server.py $d $n $byte; sleep 100; exit"
gnome-terminal --title="Aggregator" -- bash -c "python agg.py $n $d $byte; sleep 100; exit"&
TERMINAL_PID=$!

echo "Correct sum: $sum"

sleep 3
