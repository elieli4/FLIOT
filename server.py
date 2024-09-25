import socket
import pickle
import numpy as np
import csv
from collections import Counter
import sys
import time

if len(sys.argv) < 4:
    print("Usage: python server.py <i> <j> <byte>")
    sys.exit(1)

d = int(sys.argv[1])
n = int(sys.argv[2])
byte= int(sys.argv[3])
rcv=0
snt=0

p=324618072743403458035340044772650132096881761

total_clients = d * n

# Function to handle receiving sums from the aggregator
def receive_sums(host='0.0.0.0', port=12346):
    global rcv
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((host, port))
        server.listen(1)  # Listen for one connection
        print(f"Main server listening on {host}:{port}")

        client_socket, addr = server.accept()
        print(f"Accepted connection from {addr}")

        # Receive serialized sums
        sums_serialized = b''
        while True:
            data = client_socket.recv(4096)
            if not data:
                break
            sums_serialized += data
            rcv += len(data)
        # Deserialize sums
        sums_first, sums_second = pickle.loads(sums_serialized)

        # Debug check
        #print("Received sums:")
        #print("Sum First:")
        #print(sums_first)
        #print("Sum Second:")
        #print(sums_second)
        return sums_first, sums_second
    except Exception as e:
        print(f"Error receiving sums: {e}")
    finally:
        client_socket.close()
        server.close()

# Compute
def compute_Ms(ks, xs, kprimes, ys):
    ms = np.zeros((d,n))
    k = 1 #change this value
    st = time.time()
    k1 = sum(ks[0])
    k1prime = sum(kprimes[0])
    ff = xs[0][0]-k1
    kk = ys[0][0]-k1prime
    en = time.time()
    ti=str(en-st)+"\n"
    file = open("singleSumTimeBench.csv", "a")
    file.write(ti)  
    file.close()
    start = time.time()
    for i in range(0,d):
        if i==0:
            stt=time.time()
        for j in range(0,n):
            m = (xs[i][j]-k1+ks[0][j]-ks[i][j])%p
            y_test = (k1prime-kprimes[0][j]+kprimes[i][j]+k*m)%p
            if (ys[i][j])%p == y_test:
                ms[i][j]=m
            else:
                print("checksum not verified")
                print(y_test, ys[i][j])
                print(m, xs[i][j], k1, ks[0][j], ks[i][j])
                return -1
        if i==0:
            enn = time.time()
            ff = str(enn-stt) + "\n"
            file = open("singleBench.csv", "a")
            file.write(ff)
            file.close()
    end=time.time()
    ti = str(end-start) +","
    file = open("bench.csv", "a")
    file.write(ti)
    file.close()
    return ms

def find_honest_sum(ms):
    h = [None] * n
    print(ms)
    start =time.time()
    for j in range(0,n):
        #count=Counter(ms[:,j])
        count=Counter([row[j] for row in ms])
        mce, _ = count.most_common(1)[0]
        #index = np.where(ms[:,j]==mce)[0][0]
        index = np.where([row[j] for row in ms]==mce)[0][0]
        h[j]=index
    countt = Counter(h)
    firstLineHonest = countt[0]

    e=h
    end=time.time()
    ti = str(end-start) +","
    file = open("bench.csv", "a")
    file.write(ti)                      
    file.close()

    return e

def find_corruptions(ms):
    c=np.zeros((d,n))
    start = time.time()
    for j in range(0,n):
        count=Counter([row[j] for row in ms])
        mce, _ = count.most_common(1)[0]
        indices = np.where([row[j] for row in ms]!=mce)[0]
        for ind in indices:
            c[ind,j]=1
    end=time.time()
    ti = str(end-start) +","
    file = open("bench.csv", "a")
    file.write(ti)                      
    file.close()
    return c


def send_h(h, host='127.0.0.1', port=12347):
    global snt
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((host, port))
        
        # Serialize the h array using pickle
        h_serialized = pickle.dumps(h)
        client.sendall(h_serialized)
        print(len(h_serialized))
        snt += len(h_serialized)
        print("Array h sent to the aggregator.")  # Debug print
        
    except Exception as e:
        print(f"Error sending h to the aggregator: {e}")
    finally:
        client.close()

def receive_honest_sum(host='0.0.0.0', port=12346):
    global rcv
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((host, port))
        server.listen(1)  # Listen for one connection
        print(f"Main server listening on {host}:{port}")

        client_socket, addr = server.accept()
        print(f"Accepted connection from {addr}")

        # Receive serialized new arrays
        new_arrays_serialized = b''
        while True:
            data = client_socket.recv(4096)
            if not data:
                break
            new_arrays_serialized += data
            rcv += len(data)
        # Deserialize new arrays
        new_sums_first, new_sums_second = pickle.loads(new_arrays_serialized)
        
        # Convert lists to numpy arrays
        #new_sums_first = np.array(new_sums_first)
        #new_sums_second = np.array(new_sums_second)

        print("Received new sums:")
        print("New Sum First:")
        print(new_sums_first)
        print("New Sum Second:")
        print(new_sums_second)
        return new_sums_first, new_sums_second
    except Exception as e:
        print(f"Error receiving new sums: {e}")
    finally:
        client_socket.close()
        server.close()

def testing_checksum(sumh, sumy, h, kprimes):
    kprime = 0
    k = 1
    for i in range(0,n):
        kprime += kprimes[h[i]][i]
    if (sumh*k+kprime)%p==sumy:
        return True
    return False


def decrypt_honest_sum(sumx, h, ks):
    k = 0
    for i in range(0,n):
        k += ks[h[i]][i]
    sumh = (sumx-k)%p
    return sumh

if __name__ == "__main__":
    xs, ys = receive_sums()
    print(type(xs[0][0]))
    #ks = np.array(list(csv.reader(open("ks.csv"))))
    #kprimes = np.array(list(csv.reader(open("kprimes.csv"))))
    #ks = np.transpose(np.genfromtxt("ks.csv", delimiter=","))
    #kprimes = np.transpose(np.genfromtxt("kprimes.csv", delimiter=","))
    with open("ks.csv", newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        ks = [[int(value) for value in row] for row in reader]
    ks = list(map(list, zip(*ks)))
    with open("kprimes.csv", newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        kprimes = [[int(value) for value in row] for row in reader]
    kprimes = list(map(list, zip(*kprimes)))
    ms = compute_Ms(ks, xs, kprimes, ys)

    e = find_honest_sum(ms)
    c = find_corruptions(ms)

    print(c)

    print(len(e))
    send_h(e)
    sumx,sumy = receive_honest_sum()
    start = time.time()
    sumh = decrypt_honest_sum(sumx, e, ks)
    if testing_checksum(sumh, sumy, e, kprimes):
        print("FINAL HONEST SUM: ", sumh)
    else:
        print("honest checksum not verified", sumh, sumy)
    end=time.time()
    ti = str(end-start) +","
    file = open("bench.csv", "a")
    file.write(ti)
    file.close()
    print(rcv, snt)
    file = open("bytesServer.csv","a")
    file.write(str(rcv)+","+str(snt)+"\n")
    file.close()
    print("finished")
