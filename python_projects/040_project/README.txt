Password Manager
==============

Project Structure:
----------------
040_project/
├── password_manager.py    # Main program file
├── passwords.enc         # Encrypted passwords storage (created on first run)
├── master.hash          # Master password hash storage (created on first run)
└── README.txt           # This file

Requirements:
------------
1. Python 3.7 or higher
2. Required Python packages:
   - cryptography
   - pyperclip

Installation:
------------
1. Install the required packages using pip:
   pip install cryptography pyperclip

Running the Program:
------------------
1. Navigate to the project directory:
   cd Python/python_projects/040_project

2. Run the password manager:
   python password_manager.py

Classes:
-------
1. PasswordEncryption
   - Handles encryption/decryption of passwords
   - Uses Fernet symmetric encryption

2. PasswordGenerator
   - Generates secure random passwords
   - Customizable length and character types

3. PasswordManager
   - Main class managing all password operations
   - Handles file operations and user interface

Features:
--------
1. Add Password
   - Store passwords for different services
   - Auto-generate secure passwords
   - Manual password entry option

2. Get Password
   - Retrieve and copy passwords to clipboard
   - Auto-clear clipboard after 30 seconds

3. List Services
   - View all stored services
   - Show usernames and timestamps

4. Generate Password
   - Create strong random passwords
   - Customizable length and complexity

5. Delete Password
   - Remove stored passwords
   - Confirmation required

6. Check Password Strength
   - Evaluate password security
   - Multiple criteria checking

Security Features:
----------------
- Fernet encryption for password storage
- Secure master password hashing
- Auto-clearing clipboard
- Hidden password input
- Strong password generation
- Multiple security checks

File Description:
---------------
1. passwords.enc
   - Encrypted storage of all passwords
   - JSON format after encryption
   - Created automatically

2. master.hash
   - Stores hashed master password
   - SHA-256 hashing
   - Created on first run

Important Notes:
--------------
1. Security:
   - Keep master password secure
   - Regular backups recommended
   - No password recovery option

2. Usage:
   - One master password for all entries
   - Automatic encryption/decryption
   - Clipboard integration

Troubleshooting:
--------------
1. Common Issues:
   - ModuleNotFoundError: Install required packages
   - Access Denied: Check file permissions
   - Encryption Error: Verify master password

2. Data Recovery:
   - Keep backups of passwords.enc
   - Master password is required
   - No recovery without master password

For Support:
----------
[Your contact information or repository link here]