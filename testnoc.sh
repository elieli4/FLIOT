#!/bin/bash


rm ks.csv
rm kprimes.csv
rm inputs.csv
rm checksums.csv
k=$1
n=$k
d=$2
byte=$3
l=$((2 **($byte*8)))
m=$(($l -1))
echo "d: $d, n: $n, max: $m"

#for ((i=0;i<d;i++)); do
#	for ((j=0;j<n;j++)); do
 #               r1=$(shuf -i 0-$m -n 1)
   #             r2=$(shuf -i 0-$m -n 1)
  #              echo -n "$r1," >> ks.csv
    #            echo -n "$r2," >> kprimes.csv
#	done
#	echo "" >> ks.csv
#	echo "" >> kprimes.csv
#done

#gnome-terminal -- bash -c "python server.py $d $n; sleep 1; exit"
#gnome-terminal -- bash -c "python agg.py $d $n; sleep 1; exit"&
#TERMINAL_PID=$!
#sleep 1
for ((j=0;j<n;j++)); do
	g=$(shuf -i 0-$m -n 1)
	for ((i=0;i<d;i++)); do
		r1=$(shuf -i 0-$m -n 1)
                r2=$(shuf -i 0-$m -n 1)
		echo -n "$r1," >> ks.csv
                echo -n "$r2," >> kprimes.csv
		v=$(( g + r1 ))
		c=$(( g + r2 ))
		if [ $i -eq $((d-1)) ]; then
			echo -n "$v" >> inputs.csv
			echo -n "$c" >> checksums.csv
			break
		fi
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

sleep 1
gnome-terminal -- bash -c "python server.py $d $n; sleep 3; exit"
gnome-terminal -- bash -c "python agg.py $d $n; sleep 3; exit"&
TERMINAL_PID=$!

sleep 2
