import socket
import threading
import pickle
import numpy as np

# Dictionary to hold sums of the first and second numbers from clients with ID (1, j)
sums = {'first_sum': 0, 'second_sum': 0}
# Dictionary to hold all received values
received_values = {}
# Counter to track the number of received messages
received_count = 0
# Total number of expected clients
d = 2  # Adjust this as needed
n = 3  # Adjust this as needed
total_clients = d * n

# Lock for thread-safe updates
lock = threading.Lock()

# Function to send sums to the main server
def send_sums_to_main_server(sums_first, sums_second, host='127.0.0.1', port=12346):
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((host, port))
        
        # Serialize the sums arrays using pickle
        sums_serialized = pickle.dumps((sums_first, sums_second))
        client.sendall(sums_serialized)
        
        print("Sums sent to main server.")  # Debug print
        
    except Exception as e:
        print(f"Error sending sums to main server: {e}")
    finally:
        client.close()

# Function to compute s_i,j
def compute_sums():
    s1_first_sum = sums['first_sum']
    s1_second_sum = sums['second_sum']
    
    # Initialize 2D arrays for storing sums
    sums_first = np.zeros((d + 1, n + 1))
    sums_second = np.zeros((d + 1, n + 1))

    print("Computing sums:")  # Debug print

    for i in range(2, d + 1):
        for j in range(1, n + 1):
            print(f"Checking i={i}, j={j}")  # Debug print
            key_1j = f"(1, {j})"
            key_ij = f"({i}, {j})"
            if key_1j in received_values and key_ij in received_values:
                m_1j_first, m_1j_second = received_values[key_1j]
                m_ij_first, m_ij_second = received_values[key_ij]
                s_ij_first = s1_first_sum - m_1j_first + m_ij_first
                s_ij_second = s1_second_sum - m_1j_second + m_ij_second
                sums_first[i, j] = s_ij_first
                sums_second[i, j] = s_ij_second
                print(f"s_{i},{j}_first: {s_ij_first}, s_{i},{j}_second: {s_ij_second}")  # Debug print

    # Send the computed sums to the main server
    send_sums_to_main_server(sums_first, sums_second)

# Function to handle incoming client connections
def handle_client(client_socket):
    global received_count
    try:
        message = client_socket.recv(1024).decode('utf-8')
        print(f"Received message: {message}")

        # Parse the received message
        client_id, num1, num2 = message.split(':')
        client_id = client_id.strip()
        num1 = int(num1.strip())
        num2 = int(num2.strip())

        # Store the received values
        with lock:
            received_values[client_id] = (num1, num2)
            received_count += 1

            # If the first part of the ID is 1, sum the numbers
            if client_id.startswith('(1,'):
                sums['first_sum'] += num1
                sums['second_sum'] += num2

            print(f"Current sums: {sums}")  # Debug print

            # Check if all clients have sent their messages
            if received_count >= total_clients:
                # Compute all sums s_i,j
                compute_sums()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()

# Main server function
def start_server(host='0.0.0.0', port=12345):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(total_clients)  # Adjust the backlog as needed
    print(f"Server listening on {host}:{port}")

    while True:
        client_socket, addr = server.accept()
        print(f"Accepted connection from {addr}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

if __name__ == "__main__":
    start_server()
