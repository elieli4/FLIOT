import socket
import threading
import pickle
import numpy as np
import time
import csv

# Dictionary to hold sums of the encrypted values (first_sum) and checksums (second_sums) from clients with ID (1, j)
sums = {'first_sum': 0, 'second_sum': 0}
# Dictionary to hold all received values
received_values = {}
# Counter to track the number of received messages, to check data was received from all devices
received_count = 0

# To measure bytes received and sent
rcv = 0
snt = 0

import sys
if len(sys.argv) < 3:
    print("Usage: python agg.py <#of groups> <#of devices>")
    sys.exit(1)

# d is the number of devices per group, n is the number of groups, and byte is the size of the inputs (before encryption)
d = int(sys.argv[2])
n = int(sys.argv[1])
byte= 3

# prime
p=324618072743403458035340044772650132096881761

total_clients = d * n

lock = threading.Lock()

# Function to send sums to the main server
def send_sums(sums_first, sums_second, host='127.0.0.1', port=12346):
    global snt
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((host, port))
        
        sums_serialized = pickle.dumps((sums_first, sums_second))
        client.sendall(sums_serialized)
        
        print("Sums sent to main server.")  # Debug print

        # Measure how many bytes were sent
        snt = snt + len(sums_serialized)

        # To measure baselines if needed
        #singleSum=len(pickle.dumps((sums['first_sum'],sums['second_sum'])))
        #file = open("singleSum.csv","a")
        #file.write(str(singleSum) + "\n")
        #file.close()
        print("The encrypted sums were sent to the main server.\n")
    except Exception as e:
        print(f"Error sending sums to main server: {e}")
    finally:
        client.close()
        receive_h()

# Function to compute the sums to send to the server, x^(i,j) and y^(i,j)
def compute_sums():

    # First row sums, computed here for efficiency.
    s1_first_sum = sums['first_sum']
    s1_second_sum = sums['second_sum']
    
    # Initialize arrays for storing the sums. sums_first is the sums of x, sums_second is the sums of y in the protocol
    sums_first = [[0 for _ in range(n)] for _ in range(d)]
    sums_second = [[0 for _ in range(n)] for _ in range(d)]

    print("Computing encrypted sums.")  # Debug print

    start = time.time()
    for i in range(0, d):
        #for baseline
        #if i==0:
            #stt=time.time()
        for j in range(0, n):
            # dictionary key for entry in first row and column j, or row i and column j
            key_1j = f"(0, {j})"
            key_ij = f"({i}, {j})"
            if key_1j in received_values and key_ij in received_values:
                # Encrypted messages retrieved from dictionaries
                m_1j_first, m_1j_second = received_values[key_1j]
                m_ij_first, m_ij_second = received_values[key_ij]

                # Swap value of the first row to the value in row i. See protocol.
                s_ij_first = (s1_first_sum - m_1j_first + m_ij_first)%p
                s_ij_second = (s1_second_sum - m_1j_second + m_ij_second)%p

                # Store in array
                sums_first[i][j] = s_ij_first
                sums_second[i][j] = s_ij_second
                
 #              print(f"s_{i},{j}_first: {s_ij_first}, s_{i},{j}_second: {s_ij_second}")  # Debug print
        #for baseline
        #if i==0:
            #enn = time.time()
            #ff = str(enn-stt) + "\n"
            #file = open("singleAggTimes.csv", "a")
            #file.write(ff)
            #file.close()

    # Measure execution time and write to file
    end=time.time()
    ti = str(end-start) +","
    file = open("aggTimes.csv", "a")
    file.write(ti)
    file.close
    #print(ti)

    # Send the computed sums to the main server
    send_sums(sums_first, sums_second)

# Function to handle incoming client connections. Can be bypassed for benchmarking. 
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

            #print(f"Current sums: {sums}")  # Debug print
            #print("received bytes from clients: ", rcv)
            # Check if all clients have sent their messages
            if received_count >= total_clients:
                # Compute all sums s_i,j
                compute_sums()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()

# Receive the set of honest user indices from the server.
def receive_h(host='0.0.0.0', port=12347):
    global rcv
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((host, port))
        server.listen(1)  # Listen for one connection
        print(f"Aggregator listening for h on {host}:{port}")

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
        print("Received array h containing a selection of one honest device per group from the main server.\n")
        return h
    except Exception as e:
        print(f"Error receiving h: {e}")
    finally:
        if client_socket:
            client_socket.close()
        server.close()
        compute_honest_sum(h)

# Compute the encrypted sum from only honest clients, given the set of honest clients h from the server
def compute_honest_sum(h):
    print("Computing encrypted honest sum using the received array h.")
    sumx = 0
    sumy = 0
    start = time.time()
    for j in range(0,n):
        key = f"({h[j]}, {j})"
        x, y = received_values[key]
        sumx = (sumx+x)%p
        sumy = (sumy+y)%p
    # Benchmarking execution time
    end=time.time()
    ti = str(end-start) +","
    file = open("aggTimes.csv", "a")
    file.write(ti)
    file.close()

    # Send results to server
    send_honest_sum(sumx, sumy)

# Send the encrypted honest sum + checksum to the server
def send_honest_sum(sumx, sumy, host='127.0.0.1', port=12346):
    global snt
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((host, port))
        
        # Serialize the sums arrays using pickle
        honest_sums_serialized = pickle.dumps((sumx, sumy))
        client.sendall(honest_sums_serialized)
        snt += len(honest_sums_serialized)
        print("Honest encrypted sum and checksum were sent to main server. This was the aggregator's final task.\n")  # Debug print
        
    except Exception as e:
        print(f"Error sending new arrays to main server: {e}")
    finally:
        client.close() 

# Main aggregating server function. Can be bypassed for benchmarking.
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

# Bypass of receiving values for faster benchmarking of the second phase. This assumes files with all inputs present, instead of receiving data from clients.
def get_values():

    # Reading values from files and store in arrays
    with open("inputs.csv", newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        xs = [[int(value) for value in row] for row in reader]
    xs = list(map(list, zip(*xs)))
    with open("checksums.csv", newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        ys = [[int(value) for value in row] for row in reader]
    ys = list(map(list, zip(*ys)))

    # Put the values in the dictionary
    for i in range(d):
        for j in range(n):
            client_id = f"({i}, {j})"
            num1 = xs[i][j]
            num2 = ys[i][j]
            received_values[client_id] = (num1, num2)
    #st = time.time()

    # Compute the sum for the first row only
    sums['first_sum'] = sum(xs[0])
    sums['second_sum'] = sum(ys[0])

    # benchmarking for baseline
    #en=time.time()
    #tii=en-st
    #file = open("singleSumTime.csv","a")
    #file.write(str(tii) +  "\n")
    #file.close()
    print("Clients sent their encrypted and authenticated inputs to aggregator.\n")
    compute_sums()

if __name__ == "__main__":
    # bypass this for benchmarking
   # start_server()

    # Use this for phase 2 benchmarking, assuming necessary files are present
    get_values()

    # Print and store bytes info for communication benchmarking
    print("Bytes sent/received: ",snt, rcv)
    file = open("bytesAgg.csv","a")
    file.write(str(rcv)+","+str(snt)+"\n")
    file.close()
