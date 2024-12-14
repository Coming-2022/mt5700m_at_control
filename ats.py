import socket
import time
import os

SERVER_IP = "192.168.8.1"
SERVER_PORT = 20249
BUFFER_SIZE = 2048 * 4
RETRY_DELAY = 3  # Delay time between each retry (seconds)
TIMEOUT = 120 # Setting commands timeout 120s to reconnect.

# Unix Domain Socket file path
SOCKET_FILE = "/tmp/at_socket.sock"

def send_command(client_socket, command):
    """
    Send AT command and wait for response
    """
    print(f"Sending command: {command}")
    client_socket.sendall(command.encode() + b"\r")

def receive_response(client_socket):
    """
    Receive server response and detect if it's the end flag (OK or ERROR)
    """
    response = bytearray()
    while True:
        data = client_socket.recv(BUFFER_SIZE)
        if not data:
            break  # Server closed the connection
        response.extend(data)
        decoded_response = response.decode(errors='ignore')
        if "OK" in decoded_response or "ERROR" in decoded_response:
            print(f"Received response: {decoded_response}")
            break  # Received OK or ERROR, consider the command processing is done

    return decoded_response

def handle_commands(client_socket):
    """
    Handle commands received from terminal and communicate with server
    """
    # Remove the local Unix Socket file if it exists
    if os.path.exists(SOCKET_FILE):
        os.remove(SOCKET_FILE)

    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as unix_socket:
        unix_socket.bind(SOCKET_FILE)
        unix_socket.listen(1)
        unix_socket.settimeout(TIMEOUT)
        print(f"Listening for commands on {SOCKET_FILE}")

        while True:
            try:
                conn, _ = unix_socket.accept()
                with conn:
                    command = conn.recv(1024).decode().strip()
                    if command:
                        print(f"Received command: {command}")
                        unix_socket.settimeout(TIMEOUT)  # Reset to 2 minutes timeout
                        send_command(client_socket, command)
                        response = receive_response(client_socket)

                        # Send the response back to terminal
                        if response:
                            conn.sendall(response.encode())
                        else:
                            conn.sendall(b"No response received from server")
            except socket.timeout:
                break  # No command received within 2 minutes, attempt to reconnect

def main():
    while True:
        try:
            print("Attempting to connect to server...")
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.settimeout(60)
                client_socket.connect((SERVER_IP, SERVER_PORT))
                print("Connected to server.")
                handle_commands(client_socket)
        except socket.timeout:
            print("Connection timeout, retrying...")
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(RETRY_DELAY)

if __name__ == "__main__":
    main()
