import socket
import streamlit as st
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import os
# Encryption/Decryption parameters
KEY = b"Sanket's AES key"

def decrypt_data(encrypted_data, IV):
    backend = default_backend()
    cipher = Cipher(algorithms.AES(KEY), modes.CBC(IV), backend=backend)
    decryptor = cipher.decryptor()
    
    # Unpadding
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
    unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()
    
    return unpadded_data

def receive():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    st.info(f"IPv4 Address: {ip_address}")

    host = '0.0.0.0'
    port = 5001
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(1)
    
    st.info(f"Server listening on port {port}...")
    client, addr = server.accept()
    st.info(f"Connected to {addr}")

    # Receive file name and file size
    file_info = client.recv(1024).decode('utf-8')
    file_name, file_size = file_info.split(':-:')
    file_size = int(file_size)
    
    st.info(f"File name: {file_name}")
    st.info(f"File size: {round(file_size / (1024 * 1024),1)}MB")

    client.sendall(b'ACK')

    # Receive IV
    IV = client.recv(16)

    # Receive the encrypted file data
    progress = st.progress(0)
    bytes_received = 0
    os.makedirs("received_files", exist_ok=True)

    with open(f'./received_files/received_encrypted_{file_name}', 'wb') as f:
        while bytes_received < file_size:
            data = client.recv(1024)
            if not data:
                break
            f.write(data)
            bytes_received += len(data)
            progress.progress(min(bytes_received / file_size, 1.0), text=f"Receiving Data: {round((bytes_received)/(file_size)*100)}% [{round(bytes_received / (1024 * 1024),1)}MB/{round(file_size / (1024 * 1024),1)}MB]")
    
    f.close()
    client.close()
    server.close()
    
    # Decrypt the received file
    with open(f'./received_files/received_encrypted_{file_name}', 'rb') as f:
        encrypted_data = f.read()
    
    decrypted_data = decrypt_data(encrypted_data, IV)
    
    with open(f'./received_files/received_decrypted_{file_name}', 'wb') as f:
        f.write(decrypted_data)
    
    print("File received and decrypted.")
    st.success(f"File {file_name} received and decrypted successfully!")

if __name__ == "__main__":
    st.header("Receive File")
    if st.button("Receive"):
        receive()