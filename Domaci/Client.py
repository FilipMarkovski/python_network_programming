from socket import *
import os


server_adress = 'localhost'
server_port = 2222

sock = socket(AF_INET, SOCK_STREAM)
sock.connect((server_adress, server_port))

print(sock.recv(4096).decode())


print("Odaberite jednu od opcija:\n")
print("1. Registracija\n2. Prijavljivanje\n3. Nastavak bez registracije\n>>>")
odabranoPolje = input()
sock.send(odabranoPolje.encode())
if odabranoPolje == '1':
    while True:
        print("Odaberite ime:\n>>>")
        ime = input()
        print("Odaberite lozinku:\n>>>")
        lozinka = input()
        if ":" in ime or ":" in lozinka:
            print("INVALID CHAR! Ne smete da koristite ':' u imenu i/ili lozinci!")
            continue
        sock.send('{}:{}'.format(ime, lozinka).encode())
        registracija_status = sock.recv(4096).decode()
        if registracija_status == "OK":
            print("Uspesno ste se registrovali!")
            break
        print("To ime vec postoji! Molim Vas da odaberete drugo :).")







elif odabranoPolje == '2':
    while True:
        print("Ukucajte ime:\n>>>")
        ime = input()
        print("Ukucajte lozinku:\n>>>")
        lozinka = input()
        if ":" in ime or ":" in lozinka:
            print("INVALID CHAR! Ne smete da koristite ':' u imenu i/ili lozinci!")
            continue
        sock.send('{}:{}'.format(ime, lozinka).encode())
        login_status = sock.recv(4096).decode()
        if login_status == "OK":
            print("Uspesno ste se ulogovali!")
            break
        print("Pogresili ste ime i/ili lozinku! Ponovite.")
        continue

    # U sustini izlista sve fajlove u direktorijumu korisnika
    print("\n" + "Fajlovi koji ste ranije upload-ovali na server:\n")
    fajlovi = sock.recv(4096).decode()
    print(fajlovi)

    # Putanja do korisnikovog foldera
    direktorijum = sock.recv(4096).decode()

    print("Ukucajte 1 ili 2, u zavisnosti od toga šta želite dalje:\n1.Download nekog od ovih fajlova\n2.Upload novog fajla\n>>>")
    odgovor = input()
    sock.send(odgovor.encode())
    if odgovor == '1':
        while True:
            print(fajlovi)
            print("Koji fajl zelite?")
            kljuc = input()
            if kljuc not in os.listdir(direktorijum) and '.txt' not in kljuc:
                print("Ne postoji takav fajl u ovom direktorijumu")
                continue
            direktna_putanja = '{}\\{}'.format(direktorijum, kljuc)
            sock.send(direktna_putanja.encode())
            files = sock.recv(4096).decode()
            if 'Downloads' not in os.listdir():
                os.mkdir('Downloads')
            with open('Downloads\{}'.format(kljuc), 'w+') as file:
                file.write(files)
            print("Uspesno sacuvan fajl u direktorijum Downloads\\{}".format(kljuc))
            break

    elif odgovor == '2':
        sock.send(odgovor.encode())
        print("Mozete poceti sa kucanjem vaseg fajla:")
        while True:
            tekst = input()
            if len(tekst) > 500:
                print("Ne mozete iskucati tekst koji je duzi od 500 karaktera. Molim Vas pokusajte ponovo:")
                continue
            else:
                private_key = sock.recv(4096).decode()

                with open('{}\\{}'.format(direktorijum, private_key), 'w+') as file:
                    file.write(tekst)
                print("Uspesno ste upisali fajl u Vas direktorijum!")
                print("Vas privatni kljuc je: " + private_key)

                break

    else:
        print("Pogresan unos. Probajte ponovo.")




elif odabranoPolje == '3':
    print("Preskocen proces registracije ili prijavljivanja.\nU ovom modu mozete samo skidati fajlove po unetom kljucu.\n")
    while True:
        print("Molim Vas da unesete kljuc fajla koji zelite da skinete:\n>>>")
        kljuc = input()
        if ":" in kljuc:
            print("Nedozvoljen karakter! Pokusajte ponovo")
            continue
        break
    sock.send(kljuc.encode())
    status = sock.recv(4096).decode()
    if status == '404':
        print("Error 404: File Not Found")
    else:
        print("Preuzimanje...")
        files = sock.recv(4096).decode()
        if 'Downloads' not in os.listdir():
            os.mkdir('Downloads')
        with open('Downloads\{}'.format(kljuc), 'a+') as file:
            file.write(files)
        print("Uspesno sacuvan fajl u direktorijum Downloads\\{}".format(kljuc))

else:
    print("Pogresan unos! Pokusajte ponovo :).")