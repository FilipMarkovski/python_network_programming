from socket import *
from ServerClientThread import *

# Broj porta na koji povezujemo nas soket
server_port = 2222
server_adress = 'localhost'

# Kreiramo soket
server_socket = socket(AF_INET, SOCK_STREAM)

try:
    # Pokusavamo da povezemo soket na odredjenu adresu i port
    server_socket.bind((server_adress, server_port))
    server_socket.listen(5)
    print('Cekamo klijente')
    while True:

        # Prihvatamo konekciju
        client_socket, client_adress = server_socket.accept()
        print("Klijent se povezao...")

        # Otvaramo nit za novonastale konekcije (buni se program jer nismo nigde referencirali
        ServerClientThread(client_socket)

except:
    # Print-ujemo gresku ako baci exception, ovim se obuhvata svaki exception
    print("Greska pri konekciji!")