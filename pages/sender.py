import socket
import streamlit as st
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives import keywrap
import os

# Encryption/Decryption parameters
KEY = b"Sanket's AES key"  # This should be securely managed
IV_SIZE = 16  # AES block size for CBC mode

def encrypt_data(data, IV):
    backend = default_backend()
    cipher = Cipher(algorithms.AES(KEY), modes.CBC(IV), backend=backend)
    encryptor = cipher.encryptor()
    
    # Padding
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(data) + padder.finalize()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    
    return encrypted_data

def send(file, host):
    port = 5001

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    
    # Read file and encrypt it
    file_contents = file.read()

    IV = os.urandom(IV_SIZE)
    
    encrypted_data = encrypt_data(file_contents, IV)

    # Send file name and file size
    file_name = file.name
    file_size = len(encrypted_data)
    client.sendall(f"{file_name}:-:{file_size}".encode('utf-8'))
    
    # Wait for acknowledgment
    ACK = client.recv(1024)
    if ACK != b'ACK':
        st.error("Failed to send file. Receiver did not acknowledge.")
        print("Receiver rejected the file")
        client.close()
        return
    
    client.sendall(IV)
    
    # Send encrypted data
    client.sendall(encrypted_data)
    
    client.close()
    print("File Sent Successfully!")

if __name__ == "__main__":
    st.header("Send a File")
    uploaded_file = st.file_uploader("Choose a file", type=["mp4", "txt", "jpg", "png", "pdf"])
    host = st.text_input("Enter IP Address:")
    if uploaded_file is not None:
        if st.button("Send"):
            send(uploaded_file,host)
            st.success("File Sent Successfully!")