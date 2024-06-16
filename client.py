import socket

def send_message(client_id, num1, num2, host='127.0.0.1', port=12345):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    message = f"{client_id}: {num1}: {num2}"
    client.send(message.encode('utf-8'))
    client.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 5:
        print("Usage: python client.py <i> <j> <num1> <num2>")
        sys.exit(1)
    
    i = sys.argv[1]
    j = sys.argv[2]
    num1 = sys.argv[3]
    num2 = sys.argv[4]
    client_id = f"({i}, {j})"
    
    send_message(client_id, num1, num2)
