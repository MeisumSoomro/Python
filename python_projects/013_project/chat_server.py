import socket
import threading
import json
from datetime import datetime

class ChatServer:
    def __init__(self, host='localhost', port=5555):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = {}  # {client_socket: username}
        self.messages = []
        
    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        print(f"Server started on {self.host}:{self.port}")
        
        while True:
            client_socket, address = self.server_socket.accept()
            thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            thread.start()
            
    def broadcast(self, message, sender=None):
        message_data = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'sender': sender,
            'message': message
        }
        self.messages.append(message_data)
        
        for client in self.clients:
            if client != sender:
                try:
                    client.send(json.dumps(message_data).encode())
                except:
                    self.remove_client(client)
                    
    def handle_client(self, client_socket):
        try:
            # Get username
            username = client_socket.recv(1024).decode()
            self.clients[client_socket] = username
            
            # Send welcome message
            welcome = f"{username} joined the chat!"
            self.broadcast(welcome, username)
            
            # Send last 10 messages to new client
            for message in self.messages[-10:]:
                client_socket.send(json.dumps(message).encode())
            
            while True:
                message = client_socket.recv(1024).decode()
                if message:
                    self.broadcast(message, username)
                else:
                    break
                    
        except:
            self.remove_client(client_socket)
            
    def remove_client(self, client_socket):
        if client_socket in self.clients:
            username = self.clients[client_socket]
            del self.clients[client_socket]
            client_socket.close()
            self.broadcast(f"{username} left the chat!", username)

def main():
    server = ChatServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.server_socket.close()

if __name__ == "__main__":
    main() 