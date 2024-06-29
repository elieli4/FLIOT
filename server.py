import socket
import pickle
import numpy as np
import csv
from collections import Counter

d = 5  # Adjust this as needed
n = 4  # Adjust this as needed
total_clients = d * n

# Function to handle receiving sums from the original server
def receive_sums_from_server(host='0.0.0.0', port=12346):
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

        # Deserialize sums
        sums_first, sums_second = pickle.loads(sums_serialized)

        # Convert lists to numpy arrays
        sums_first = np.array(sums_first)
        sums_second = np.array(sums_second)

        print("Received sums:")
        print("Sum First:")
        print(sums_first)
        print("Sum Second:")
        print(sums_second)
        return sums_first, sums_second
    except Exception as e:
        print(f"Error receiving sums: {e}")
    finally:
        client_socket.close()
        server.close()

def computeMs(ks, xs, kprimes, ys):
    ms = np.zeros((d,n))
    k = 1 #change this value
    k1 = sum(ks[0])
    k1prime = sum(kprimes[0])
    for j in range(0,n):
        for i in range(0,d):
            m = xs[i,j]-k1+ks[0,j]-ks[i,j]
            y_test = k1prime-kprimes[0,j]+kprimes[i,j]+k*m
            if ys[i,j] == y_test:
                ms[i,j]=m
            else:
                print("checksum not verified")
                return -1
    return ms

def findHonestSum(ms):
    h = [None] * n
    print(ms)
    for j in range(0,n):
        count=Counter(ms[:,j])
        mce, _ = count.most_common(1)[0]
        index = np.where(ms[:,j]==mce)[0][0]
        h[j]=index
    countt = Counter(h)
    firstLineHonest = countt[0]
    if firstLineHonest == n:
        e = None
        y = ms[0,0]
    elif firstLineHonest == n-1:
        e=None
        index=0
        for i in range(0,n):
            if h[i]!=0:
                index=h[i]
        y=ms[index,0]
    else:
        y=None
        e=h
    return y,e

def findCorruptions(ms):
    c=np.zeros((d,n))
    for j in range(0,n):
        count=Counter(ms[:,j])
        mce, _ = count.most_common(1)[0]
        indices = np.where(ms[:,j]!=mce)[0]
        for ind in indices:
            c[ind,j]=1
    return c


def send_h(h, host='127.0.0.1', port=12347):
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((host, port))
        
        # Serialize the h array using pickle
        h_serialized = pickle.dumps(h)
        client.sendall(h_serialized)
        
        print("Array h sent to the original server.")  # Debug print
        
    except Exception as e:
        print(f"Error sending h to the original server: {e}")
    finally:
        client.close()

def receiveHonestSums(host='0.0.0.0', port=12346):
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

        # Deserialize new arrays
        new_sums_first, new_sums_second = pickle.loads(new_arrays_serialized)

        # Convert lists to numpy arrays
        new_sums_first = np.array(new_sums_first)
        new_sums_second = np.array(new_sums_second)

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

def testingChecksum(sumh, sumy, h, kprimes):
    kprime = 0
    k = 1
    for i in range(0,n):
        kprime += kprimes[h[i],i]
    if (sumh*k+kprime)==sumy:
        return True
    return False


def decryptHonestSum(sumx, h, ks):
    k = 0
    for i in range(0,n):
        k += ks[h[i], i]
    sumh = sumx-k
    return sumh

if __name__ == "__main__":
    xs, ys = receive_sums_from_server()
    #ks = np.array(list(csv.reader(open("ks.csv"))))
    #kprimes = np.array(list(csv.reader(open("kprimes.csv"))))
    ks = np.genfromtxt("ks.csv",delimiter=",")
    kprimes = np.genfromtxt("kprimes.csv", delimiter=",")
    ms = computeMs(ks, xs, kprimes, ys)
    y,e = findHonestSum(ms)
    c = findCorruptions(ms)
    print(y,e)
    print(c)
    send_h(e)
    sumx,sumy = receiveHonestSums()
    sumh = decryptHonestSum(sumx, e, ks)
    if testingChecksum(sumx, sumy, e, kprimes):
        print("FINAL HONEST SUM: ", sumh)
    else:
        print("checksum not verified")
    print("finished")
