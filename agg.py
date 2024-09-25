import socket
import threading
import pickle
import numpy as np
import time
import csv

# Dictionary to hold sums of the first and second numbers from clients with ID (1, j)
sums = {'first_sum': 0, 'second_sum': 0}
# Dictionary to hold all received values
received_values = {}
# Counter to track the number of received messages
received_count = 0
# Total number of expected clients

rcv = 0
snt = 0

import sys
if len(sys.argv) < 4:
    print("Usage: python agg.py <i> <j> <byte>")
    sys.exit(1)

d = int(sys.argv[1])
n = int(sys.argv[2])
byte= int(sys.argv[3])

#if byte ==1:
 #   p=256019
#elif byte ==2:
 #   p=65536043
#elif byte ==3:
 #   p=16777216019
#else: #byte==4
 #   p=429496729609

p=324618072743403458035340044772650132096881761

total_clients = d * n

# Lock for thread-safe updates
lock = threading.Lock()

# Function to send sums to the main server
def send_sums_to_main_server(sums_first, sums_second, host='127.0.0.1', port=12346):
    global snt
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((host, port))
        
        # Serialize the sums arrays using pickle
        sums_serialized = pickle.dumps((sums_first, sums_second))
        client.sendall(sums_serialized)
        
        print("Sums sent to main server.")  # Debug print
        singleSum=len(pickle.dumps((sums['first_sum'],sums['second_sum'])))
        snt = snt + len(sums_serialized)
        file = open("singleSum.csv","a")
        file.write(str(singleSum) + "\n")
        file.close()

    except Exception as e:
        print(f"Error sending sums to main server: {e}")
    finally:
        client.close()
        receive_h()

# Function to compute s_i,j
def compute_sums():
    s1_first_sum = sums['first_sum']
    s1_second_sum = sums['second_sum']
    
    # Initialize 2D arrays for storing sums
   # sums_first = np.zeros((d, n))
    #sums_second = np.zeros((d, n))
    sums_first = [[0 for _ in range(n)] for _ in range(d)]
    sums_second = [[0 for _ in range(n)] for _ in range(d)]

    print("Computing sums:")  # Debug print

    start = time.time()
    for i in range(0, d):
        if i==0:
            stt=time.time()
        for j in range(0, n):
#            print(f"Checking i={i}, j={j}")  # Debug print
            key_1j = f"(0, {j})"
            key_ij = f"({i}, {j})"
            if key_1j in received_values and key_ij in received_values:
                m_1j_first, m_1j_second = received_values[key_1j]
                m_ij_first, m_ij_second = received_values[key_ij]
                s_ij_first = (s1_first_sum - m_1j_first + m_ij_first)%p
                s_ij_second = (s1_second_sum - m_1j_second + m_ij_second)%p
                sums_first[i][j] = s_ij_first
                sums_second[i][j] = s_ij_second
 #               print(f"s_{i},{j}_first: {s_ij_first}, s_{i},{j}_second: {s_ij_second}")  # Debug print
        if i==0:
            enn = time.time()
            ff = str(enn-stt) + "\n"
            file = open("singleAggTimes.csv", "a")
            file.write(ff)
            file.close()
    end=time.time()
#    print(type(s1_first_sum))
    ti = str(end-start) +","
    file = open("aggTimes.csv", "a")
    file.write(ti)
    file.close
    print(ti)
    #single sume compute time:

    # Send the computed sums to the main server
    send_sums_to_main_server(sums_first, sums_second)

# Function to handle incoming client connections
def handle_client(client_socket):
    global rcv
    global received_count
    try:
        data = client_socket.recv(1024)
        message = data.decode('utf-8')
        print(f"Received message: {message}")
        rcv += len(data)
        # Parse the received message
        client_id, num1, num2 = message.split(':')
        client_id = client_id.strip()
        num1 = int(num1.strip())
        num2 = int(num2.strip())

        # Store the received values
        with lock:
            received_values[client_id] = (num1, num2)
            received_count += 1

            # If the first part of the ID is 0, sum the numbers
            if client_id.startswith('(0,'):
                sums['first_sum'] = (sums['first_sum']+num1)%p
                sums['second_sum'] = (sums['second_sum']+num2)%p

            print(f"Current sums: {sums}")  # Debug print
            print("received bytes from clients: ", rcv)
            # Check if all clients have sent their messages
            if received_count >= total_clients:
                # Compute all sums s_i,j
                compute_sums()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()

def receive_h(host='0.0.0.0', port=12347):
    global rcv
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((host, port))
        server.settimeout(2)
        server.listen(1)  # Listen for one connection
        print(f"Original server listening for h on {host}:{port}")

        client_socket, addr = server.accept()
        print(f"Accepted connection from {addr}")

        # Receive serialized h
        h_serialized = b''
        while True:
            data = client_socket.recv(4096)
            if not data:
                break
            h_serialized += data
            rcv += len(data)
        # Deserialize h
        h = pickle.loads(h_serialized)
        print("Received array h from the main server.")
        return h
    except socket.timeout:
        print(snt, rcv)
        file = open("bytesAgg.csv","a")
        file.write(str(rcv)+","+str(snt) +"\n")
        file.close()
        print("timeout")
        if client_socket:
            client_socket.close()
        server.close()
        sys.exit(1)
    except Exception as e:
        print(f"Error receiving h: {e}")
    finally:
        if client_socket:
            client_socket.close()
        server.close()
        computeHonestSum(h)

def computeHonestSum(h):
    sumx = 0
    sumy = 0
    start = time.time()
    for j in range(0,n):
        key = f"({h[j]}, {j})"
        x, y = received_values[key]
        sumx = (sumx+x)%p
        sumy = (sumy+y)%p
    end=time.time()
    ti = str(end-start) +","
    file = open("aggTimes.csv", "a")
    file.write(ti)
    file.close()
    sendHonestSum(sumx, sumy)

def sendHonestSum(sumx, sumy, host='127.0.0.1', port=12346):
    global snt
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((host, port))
        
        # Serialize the new sums arrays using pickle
        new_sums_serialized = pickle.dumps((sumx, sumy))
        client.sendall(new_sums_serialized)
        snt += len(new_sums_serialized)
        print("New arrays sent to main server.")  # Debug print
        
    except Exception as e:
        print(f"Error sending new arrays to main server: {e}")
    finally:
        client.close() 

# Main server function
def start_server(host='0.0.0.0', port=12345):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(total_clients)  # Adjust the backlog as needed
    print(f"Server listening on {host}:{port}")

    while True:
        client_socket, addr = server.accept()
        print(f"Accepted connection from {addr}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

def get_values():
    #xs = np.transpose(np.genfromtxt("inputs.csv", delimiter=",",dtype=int))
    #ys = np.transpose(np.genfromtxt("checksums.csv", delimiter=",",dtype=int))
    with open("inputs.csv", newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        xs = [[int(value) for value in row] for row in reader]
    xs = list(map(list, zip(*xs)))
    with open("checksums.csv", newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        ys = [[int(value) for value in row] for row in reader]
    ys = list(map(list, zip(*ys)))

    for i in range(d):
        for j in range(n):
            client_id = f"({i}, {j})"
            num1 = xs[i][j]
            num2 = ys[i][j]
#            print(type(num1))
            received_values[client_id] = (num1, num2)
    st = time.time()
    sums['first_sum'] = sum(xs[0])
    sums['second_sum'] = sum(ys[0])
    en=time.time()
    tii=en-st
    file = open("singleSumTime.csv","a")
    file.write(str(tii) +  "\n")
    file.close()
    compute_sums()

if __name__ == "__main__":
   # start_server()
    get_values()
    print(snt, rcv)
    file = open("bytesAgg.csv","a")
    file.write(str(rcv)+","+str(snt)+"\n")
    file.close()
