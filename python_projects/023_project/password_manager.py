import PySimpleGUI as sg
from cryptography.fernet import Fernet
import json
import os
from typing import Dict, Optional

class PasswordManager:
    def __init__(self):
        self.key_file = "key.key"
        self.password_file = "passwords.enc"
        self.fernet = self._load_or_create_key()
        self.passwords: Dict[str, str] = self._load_passwords()

    def _load_or_create_key(self) -> Fernet:
        if os.path.exists(self.key_file):
            with open(self.key_file, "rb") as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, "wb") as f:
                f.write(key)
        return Fernet(key)

    def _load_passwords(self) -> Dict[str, str]:
        if not os.path.exists(self.password_file):
            return {}
        try:
            with open(self.password_file, "rb") as f:
                encrypted_data = f.read()
            decrypted_data = self.fernet.decrypt(encrypted_data)
            return json.loads(decrypted_data)
        except:
            return {}

    def save_password(self, service: str, password: str) -> None:
        self.passwords[service] = password
        self._save_to_file()

    def get_password(self, service: str) -> Optional[str]:
        return self.passwords.get(service)

    def _save_to_file(self) -> None:
        encrypted_data = self.fernet.encrypt(json.dumps(self.passwords).encode())
        with open(self.password_file, "wb") as f:
            f.write(encrypted_data)

def main():
    pm = PasswordManager()
    
    layout = [
        [sg.Text("Password Manager", font=("Helvetica", 16))],
        [sg.Text("Service:"), sg.Input(key="-SERVICE-")],
        [sg.Text("Password:"), sg.Input(key="-PASSWORD-", password_char="*")],
        [sg.Button("Save"), sg.Button("Retrieve"), sg.Button("Exit")]
    ]

    window = sg.Window("Password Manager", layout)

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED or event == "Exit":
            break
        
        if event == "Save":
            service = values["-SERVICE-"]
            password = values["-PASSWORD-"]
            if service and password:
                pm.save_password(service, password)
                sg.popup("Password saved successfully!")
            else:
                sg.popup("Please enter both service and password!")

        if event == "Retrieve":
            service = values["-SERVICE-"]
            if service:
                password = pm.get_password(service)
                if password:
                    sg.popup(f"Password for {service}: {password}")
                else:
                    sg.popup(f"No password found for {service}")
            else:
                sg.popup("Please enter a service name!")

    window.close()

if __name__ == "__main__":
    main() 