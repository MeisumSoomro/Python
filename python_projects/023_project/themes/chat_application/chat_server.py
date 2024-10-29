import socket
import threading
import json
from typing import Dict, Set
from datetime import datetime

class ChatServer:
    def __init__(self, host: str = 'localhost', port: int = 5555):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients: Dict[socket.socket, str] = {}  # socket: username
        self.rooms: Dict[str, Set[socket.socket]] = {"General": set()}
        
    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        print(f"Server started on {self.host}:{self.port}")
        
        while True:
            client_socket, address = self.server_socket.accept()
            print(f"Connection from {address}")
            thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            thread.start()
    
    def broadcast(self, message: str, room: str = "General", exclude: socket.socket = None):
        message_data = {
            "type": "message",
            "content": message,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "room": room
        }
        
        for client in self.rooms[room]:
            if client != exclude:
                try:
                    client.send(json.dumps(message_data).encode())
                except:
                    self.remove_client(client)

    def handle_client(self, client_socket: socket.socket):
        try:
            # Get username
            username_data = json.loads(client_socket.recv(1024).decode())
            username = username_data["content"]
            self.clients[client_socket] = username
            self.rooms["General"].add(client_socket)
            
            # Notify others
            self.broadcast(f"{username} joined the chat", exclude=client_socket)
            
            while True:
                try:
                    message = json.loads(client_socket.recv(1024).decode())
                    if message["type"] == "message":
                        self.broadcast(
                            f"{username}: {message['content']}", 
                            message.get("room", "General")
                        )
                except:
                    break
                    
        except:
            pass
        finally:
            self.remove_client(client_socket)
    
    def remove_client(self, client_socket: socket.socket):
        if client_socket in self.clients:
            username = self.clients[client_socket]
            del self.clients[client_socket]
            for room in self.rooms.values():
                room.discard(client_socket)
            self.broadcast(f"{username} left the chat")
            client_socket.close()

if __name__ == "__main__":
    server = ChatServer()
    server.start() 