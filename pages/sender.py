import socket
import streamlit as st
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import os

KEY = b"Sanket's AES key"
IV_SIZE = 16

def encrypt_data(data, IV):
    try:
        backend = default_backend()
        cipher = Cipher(algorithms.AES(KEY), modes.CBC(IV), backend=backend)
        encryptor = cipher.encryptor()
        
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(data) + padder.finalize()
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        
        return encrypted_data
    except Exception as e:
        st.error(f"Encryption failed: {e}")
        return None

def send(file, host):
    try:
        port = 5001

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((host, port))
        
        file_contents = file.read()
        IV = os.urandom(IV_SIZE)

        encrypted_data = encrypt_data(file_contents, IV)

        if encrypted_data is None:
            st.error("Encryption failed. File not sent.")
            client.close()
            return

        file_name = file.name
        file_size = len(encrypted_data)
        client.sendall(f"{file_name}:-:{file_size}".encode('utf-8'))
        
        ACK = client.recv(1024)
        if ACK != b'ACK':
            st.error("Failed to send file. Receiver did not acknowledge.")
            print("Receiver rejected the file")
            client.close()
            return
        
        client.sendall(IV)
        client.sendall(encrypted_data)

        received = client.recv(1024)
        if received == b'ACK':
            client.close()
            print("File Sent Successfully!")
            st.success("File Sent Successfully!")
    except Exception as e:
        st.error(f"An error occurred while sending the file: {e}")

if __name__ == "__main__":
    st.header("Send a File")
    uploaded_file = st.file_uploader("Choose a file", type=["mp4", "txt", "jpg", "png", "pdf"])
    host = st.text_input("Enter IP Address:")
    if uploaded_file is not None:
        if st.button("Send"):
            send(uploaded_file, host)