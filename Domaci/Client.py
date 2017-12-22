from socket import *
import os


server_address = 'localhost'
server_port = 2222

sock = socket(AF_INET, SOCK_STREAM)
sock.connect((server_address, server_port))

# Ocekujemo obavestenje o uspostavljenoj vezi
print(sock.recv(4096).decode())

# Funkcija za slucaj da korisnik zeli u bilo kom trenutku kada izvrsava unos u konzoli da prekine komunikaciju
def izlaz(konzola):
    if '/quit' in konzola:
        print("Prekida se izvrsavanje programa. Dovidjenja.")
        exit()

# Jednostavna login forma, gde dajemo 3 slucaja.
# Za prvi slucaj se registruje na serveru, upisuje se u bazu korisnika i trazi se od njega da se ponovo poveze na server
# kako bi se ulogovao (na neki nacin validacija preko mejla sto se radi - ponovno prijavljivanje na server)
print("Odaberite jednu od opcija:\n")
print("1. Registracija\n2. Prijavljivanje\n3. Nastavak bez registracije\n>>>")

odabranoPolje = input()

# Saljemo serveru informaciju o tome koja opcija je odabrana. Takodje, proverava se da li je korisnik hteo da izadje.
sock.send(odabranoPolje.encode())
izlaz(odabranoPolje)

########################################################################################################################

# Registracija
if odabranoPolje == '1':
    while True:
        ime = input("Ukucajte ime (ne smete da unesete prazan tekst!):\n>>>")
        izlaz(ime)
        lozinka = input("Ukucajte lozinku (ne smete da unesete prazan tekst!):\n>>>")
        izlaz(lozinka)

        # Ne dozvoljavamo da korisnik samo pritisne enter kad mu se zatrazi da unese ime i lozinku.
        # Isto tako se ne dozvoljava ':' karakter jer je to separator u nasoj bazi.
        if ":" in ime or ":" in lozinka or ime == "" or lozinka == "" or " " in ime or " " in lozinka:
            print("INVALID CHAR! Ne smete da koristite ':' u imenu i/ili lozinci!")
            continue

        # Ovako je formatirana baza: ime:lozinka
        sock.send('{}:{}'.format(ime, lozinka).encode())

        # Dobijamo info od servera da li smo uspesno upisani u bazu.
        registracija_status = sock.recv(4096).decode()
        if registracija_status == "OK":
            print("Uspesno ste se registrovali!")
            break
        print("To ime vec postoji! Molim Vas da odaberete drugo :).")

########################################################################################################################

# Login
elif odabranoPolje == '2':
    while True:
        ime = input("Ukucajte ime:\n>>>")
        izlaz(ime)
        lozinka = input("Ukucajte lozinku:\n>>>")
        izlaz(lozinka)

        # Ovde nismo morali da proveravamo da li korisnik nista nije uneo jer se svejedno 'provali'.
        # Pozeljno je, ali necemo jos veci 'dzumbus' od koda da pravimo
        if ":" in ime and ":" in lozinka:
            print("INVALID CHAR!")
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

    # Isti slucaj kao i za ranije unose. Salje se odgovor serveru i proverava se da li je korisnik uneo '/quit'
    odgovor = input()
    sock.send(odgovor.encode())
    izlaz(odgovor)

    # Download odabrano
    if odgovor == '1':
        while True:
            print(fajlovi)
            print("Koji fajl zelite?")

            # Fajlovi su imenovani po kljucevima. Time ne moramo da zakomplikujemo sam sadrzaj fajlova.
            # Pomocu JSON-a mozemo svakako uraditi, ali izabran je laksi nacin.
            # Korisnici imaju svoje foldere na serveru i mogu da pristupaju svojim fajlovima.
            kljuc = input()
            izlaz(kljuc)

            # Ako slucajno se napravi greska u kucanju ili korisnik nije uneo ekstenziju fajla
            # Ovo je ako postoje .html, .txt ili obicni fajlovi i sl.
            if kljuc not in os.listdir(direktorijum) and '.txt' not in kljuc:
                print("Ne postoji takav fajl u ovom direktorijumu")
                continue

            # Pravimo citavu putanju do tog fajla i saljemo serveru za zahtev
            direktna_putanja = '{}\\{}'.format(direktorijum, kljuc)
            sock.send(direktna_putanja.encode())

            # Dobijamo sadrzaj fajlova i pravimo Downloads folder ukoliko vec ne postoji.
            files = sock.recv(4096).decode()
            if 'Downloads' not in os.listdir():
                os.mkdir('Downloads')

            # Za kasnije verzije aplikacije, moze da se implementira da pravi duplikate od fajlova koje skidamo.
            # Za sad samo 'gazi' prethodne verzije, tako da obratite paznju na to!
            with open('Downloads\{}'.format(kljuc), 'w+') as file:
                file.write(files)
            print("Uspesno sacuvan fajl u direktorijum Downloads\\{}".format(kljuc))
            break

    # Upload odabrano
    elif odgovor == '2':
        print("Mozete poceti sa kucanjem vaseg fajla:")
        while True:
            tekst = input()
            izlaz(tekst)
            if len(tekst) > 500:
                print("Ne mozete iskucati tekst koji je duzi od 500 karaktera. Molim Vas pokusajte ponovo:")
                continue
            else:

                # Ako uspesno unesemo tekst, dobijamo nas kljuc (ime fajla)
                private_key = sock.recv(4096).decode()

                with open('{}\\{}'.format(direktorijum, private_key), 'w+') as file:
                    file.write(tekst)
                print("Uspesno ste upisali fajl u Vas direktorijum!")
                print("Vas privatni kljuc je: " + private_key)

                break

    else:
        # Ako pogresnu opciju unesemo, korisnik se izbacuje iz komunikacije sa serverom.
        # Sve ovo je moglo u jos jedan while da se stavi kako bi se vratio na unos, ali tek onda kod ne bi bio citljiv
        # Ostaje za kasnije verzije da se implementira
        print("Pogresan unos. Probajte ponovo.")

########################################################################################################################

# Imamo vec kljuc, trazimo neki specificni fajl. Ovo je inace, za sad, jedini nacin da dodjemo do bilo kog fajla.
# Naravno ukoliko posedujemo taj kljuc, inace necemo dobiti listu svih fajlova.
elif odabranoPolje == '3':
    print("Preskocen proces registracije ili prijavljivanja.\nU ovom modu mozete samo skidati fajlove po unetom kljucu.\n")
    while True:
        print("Molim Vas da unesete kljuc fajla koji zelite da skinete:\n>>>")
        kljuc = input()
        izlaz(kljuc)
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