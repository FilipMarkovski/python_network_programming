from threading import *
import os
import string
import random

# Klasa u zagradama znaci da nasleđujemo klasu Thread iz modula threading
class ServerClientThread(Thread):

    # Konstruktor klase
    def __init__(self, client_socket):
        # postavljamo atribute
        self.socket = client_socket
        # Pozivamo konstruktor nadredjene klase (Thread klase u ovom slucaju)
        super().__init__()
        # pokrecemo nit
        self.start()

    def run(self):
        self.socket.send("Uspesno ste se povezali!".encode())
        # Prvo saljemo serveru info o odabranom polju
        odabranoPolje = self.socket.recv(4096).decode()

        if odabranoPolje == '1':
            registrovan = False
            while not registrovan:
                ime, lozinka = self.socket.recv(4096).decode().split(":")
                with open("baza_korisnika.txt", "r+") as baza:
                    linije_baze = baza.readlines()
                    for info in linije_baze:
                        if ime == info.split(":")[0]:
                            self.socket.send("FAIL".encode())
                            registrovan = False
                            break
                        registrovan = True
                    if registrovan:
                        baza.write("{}:{}\n".format(ime,lozinka))
                        self.socket.send("OK".encode())








        elif odabranoPolje == '2':

            # Postavljamo kontrolnu promenljivu, kako bismo izasli iz while petlje
            ulogovan = False
            while not ulogovan:

                # Izvlacimo iz JSON-a podatke korisnika
                ime, lozinka = self.socket.recv(4096).decode().split(":")

                # Otvaramo bazu korisnika i citamo liniju po liniju (tj. jednog po jednog korisnika)
                with open("baza_korisnika.txt", "r+") as baza:
                    linije_baze = baza.readlines()
                    for info in linije_baze:
                        baza_ime, baza_lozinka = info.split(":")
                        baza_lozinka = baza_lozinka.replace("\n", "")
                        if ime == baza_ime and lozinka == baza_lozinka:
                            self.socket.send("OK".encode())
                            ulogovan = True
                            break
                        ulogovan = False

                # Ako nije uopste usao u if, korisnik uopste nije ulogovan i morace ponovo da se uloguje
                if not ulogovan:
                    self.socket.send("FAIL".encode())

            # Cuvamo direktorijum 'Shared Files' u promenljivu zbog citljivijeg koda
            shared_dir = 'Shared Files'

            # Ako taj direktorijum ne postoji, napravicemo ga
            if shared_dir not in os.listdir():
                os.mkdir(shared_dir)

            # Proveravamo da li svaki registrovan korisnik ima svoj direktorijum, ako nema - pravimo ga
            with open("baza_korisnika.txt", "r+") as baza:
                linije_baze = baza.readlines()
                for info in linije_baze:
                    registrovani_korisnici = info.split(":")[0]
                    if registrovani_korisnici not in os.listdir(shared_dir):
                        os.mkdir(shared_dir + "\\" + registrovani_korisnici)

            # Fajlovi direktorijuma ulogovanog korisnika
            files = os.listdir(shared_dir + "\\" + ime)

            # Pretvara listu u string (takoreci "join-uje" je u string, ako nema nista u tom folderu - izbacuje 'EMPTY'
            send_data = '\n'.join(files) if files else 'EMPTY'

            # Cuvamo putanju do korisnikovog foldera u promenljivu
            putanja = shared_dir + "\\" + ime

            # Saljemo spisak fajlova u folderu korisnika
            self.socket.send(send_data.encode())

            # Saljemo putanju foldera 'na cuvanje'
            self.socket.send(putanja.encode())


            odgovor = self.socket.recv(4096).decode()
            if odgovor == '1':
                print("Download izabrano")
                direktna_putanja = self.socket.recv(4096).decode()
                with open(direktna_putanja, 'rb') as download:
                    self.socket.sendall(download.read())
                print("Fajl uspesno poslat!")


            elif odgovor == '2':
                print("Upload izabrano")
                def id_generator(size=6, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
                    return ''.join(random.choice(chars) for _ in range(size))
                id_postoji = False
                while not id_postoji:
                    randomizer = id_generator()
                    for root, dirs, files in os.walk(shared_dir):
                        for name in files:
                            if randomizer in name:
                                print("Taj kljuc vec postoji")
                                id_postoji = True
                    if not id_postoji:
                        self.socket.send(randomizer.encode())
                        break
                    else:
                        continue

            else:
                print("Pogresan unos!")







        elif odabranoPolje == '3':
            shared_dir = 'Shared Files'
            kljuc = self.socket.recv(4096).decode()
            kljuc = kljuc.replace('\n', "")
            # print(kljuc)
            print("Sad cemo da trazimo fajl\n")
            pronadjen_fajl = False
            file_path = None
            for root, dirs, files in os.walk(shared_dir):
                for name in files:
                    if kljuc in name:
                        print("Pronadjen %s" % name)
                        pronadjen_fajl = True
                        file_path = ''.join(root) + "\\" + '\n'.join(files)
                        self.socket.send("OK".encode())
                        break

            if not pronadjen_fajl:
                print("404 File Not Found")
                self.socket.send("404".encode())
            else:
                with open(file_path, 'rb') as download:
                    self.socket.sendall(download.read())
                print("Fajl uspesno poslat!")