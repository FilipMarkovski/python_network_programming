from socket import *
from ServerClientThread import *

server_port = 2222
server_adress = 'localhost'
# Kreiramo soket
server_socket = socket(AF_INET,SOCK_STREAM)

try:
    server_socket.bind((server_adress, server_port))
    server_socket.listen(5)
    print('Cekamo klijente')
    while True:
        client_socket, client_adress = server_socket.accept()
        print("Klijent se povezao...")
        ServerClientThread(client_socket)
except AttributeError:
    print("Greska!")