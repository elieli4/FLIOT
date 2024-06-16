import socket
import pickle
import numpy as np

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

    except Exception as e:
        print(f"Error receiving sums: {e}")
    finally:
        client_socket.close()
        server.close()

if __name__ == "__main__":
    receive_sums_from_server()
