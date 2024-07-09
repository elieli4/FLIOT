import socket
import numpy as np

k=1
p=33554432039

def send_message(client_id, num1, num2, host='127.0.0.1', port=12345):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    message = f"{client_id}: {num1}: {num2}"
    client.send(message.encode('utf-8'))
    client.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 4:
        print("Usage: python client.py <i> <j> <num1>")
        sys.exit(1)
    
    i = sys.argv[1]
    j = sys.argv[2]
    num1 = int(sys.argv[3])
    num2 = k*num1
    client_id = f"({i}, {j})"

    ks = np.genfromtxt("ks.csv",delimiter=",")
    kprimes = np.genfromtxt("kprimes.csv", delimiter=",")

    enc1 = int(num1 + ks[int(i),int(j)])%p
    enc2 = int(num2 + kprimes[int(i),int(j)])%p
    
    send_message(client_id, enc1, enc2)
