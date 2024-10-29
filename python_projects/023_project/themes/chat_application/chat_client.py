import PySimpleGUI as sg
import socket
import json
import threading
from typing import Optional
from datetime import datetime

class ChatClient:
    def __init__(self):
        self.socket: Optional[socket.socket] = None
        self.connected = False
        self.username = ""
        self.current_room = "General"
    
    def connect(self, host: str, port: int, username: str) -> bool:
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
            self.username = username
            
            # Send username to server
            self.send_message(username, msg_type="username")
            self.connected = True
            return True
        except:
            return False
    
    def send_message(self, content: str, msg_type: str = "message"):
        if self.connected:
            message = {
                "type": msg_type,
                "content": content,
                "room": self.current_room,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            }
            try:
                self.socket.send(json.dumps(message).encode())
                return True
            except:
                return False
        return False

    def receive_messages(self, window):
        while self.connected:
            try:
                message = json.loads(self.socket.recv(1024).decode())
                window.write_event_value('-MESSAGE-', message)
            except:
                self.connected = False
                window.write_event_value('-DISCONNECT-', None)
                break

def create_layout():
    return [
        [sg.Text("Chat Application", font=("Helvetica", 16))],
        [
            sg.Text("Server:"), sg.Input("localhost", key="-HOST-", size=(15, 1)),
            sg.Text("Port:"), sg.Input("5555", key="-PORT-", size=(6, 1)),
            sg.Text("Username:"), sg.Input(key="-USERNAME-", size=(15, 1)),
            sg.Button("Connect")
        ],
        [
            sg.Multiline(
                size=(50, 20),
                key="-CHAT-",
                disabled=True,
                autoscroll=True,
                reroute_stdout=False,
                reroute_cprint=True
            )
        ],
        [
            sg.Input(key="-INPUT-", size=(40, 1), enable_events=True),
            sg.Button("Send", disabled=True)
        ]
    ]

def main():
    client = ChatClient()
    window = sg.Window("Chat Application", create_layout(), finalize=True)
    
    while True:
        event, values = window.read()
        
        if event == sg.WIN_CLOSED:
            break
            
        if event == "Connect":
            host = values["-HOST-"]
            port = int(values["-PORT-"])
            username = values["-USERNAME-"]
            
            if username.strip():
                if client.connect(host, port, username):
                    window["-CHAT-"].print("Connected to server!")
                    window["Send"].update(disabled=False)
                    window["Connect"].update(disabled=True)
                    
                    # Start receiving messages
                    thread = threading.Thread(
                        target=client.receive_messages,
                        args=(window,),
                        daemon=True
                    )
                    thread.start()
                else:
                    window["-CHAT-"].print("Failed to connect to server!")
            else:
                sg.popup("Please enter a username!")
                
        if event == "Send" and values["-INPUT-"].strip():
            message = values["-INPUT-"]
            if client.send_message(message):
                window["-INPUT-"].update("")
            else:
                window["-CHAT-"].print("Failed to send message!")
                
        if event == "-MESSAGE-":
            message = values[event]
            window["-CHAT-"].print(
                f"[{message['timestamp']}] {message['content']}"
            )
            
        if event == "-DISCONNECT-":
            window["-CHAT-"].print("Disconnected from server!")
            window["Send"].update(disabled=True)
            window["Connect"].update(disabled=False)
            
    window.close()

if __name__ == "__main__":
    main() 