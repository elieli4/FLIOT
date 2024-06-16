import socket
import pickle
import numpy as np
import csv
from collections import Counter

d = 2  # Adjust this as needed
n = 3  # Adjust this as needed
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
    k1 = sum(ks[1])
    k1prime = sum(kprimes[1])
    for j in range(1,n+1):
        for i in range(1,d+1):
            m = xs[i-1,j-1]-k1+ks[1-1,j-1]-ks[i-1,j-1]
            y_test = k1prime-kprimes[1-1,j-1]+kprimes[i-1,j-1]+k*m
            if ys[i-1,j-1] == y_test:
                ms[i-1,j-1]=m
            else:
                print("checksum not verified")
                return -1
    return ms

def findHonestSum(ms):
    h = [None] * n
    print(ms)
    for j in range(1,n+1):
        count=Counter(ms[:,j-1])
        mce, _ = count.most_common(1)[0]
        index = np.where(ms[:,j-1]==mce)[0][0]
        print(ms[:,j-1])
        h[j-1]=index
    return h

if __name__ == "__main__":
    xs, ys = receive_sums_from_server()
    #ks = np.array(list(csv.reader(open("ks.csv"))))
    #kprimes = np.array(list(csv.reader(open("kprimes.csv"))))
    ks = np.genfromtxt("ks.csv",delimiter=",")
    kprimes = np.genfromtxt("kprimes.csv", delimiter=",")
    ms = computeMs(ks, xs, kprimes, ys)
    h = findHonestSum(ms)
    print(h)
    print("ok")
