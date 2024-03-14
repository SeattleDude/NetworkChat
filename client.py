import socket, threading, os, base64
from cryptography import fernet
from cryptography.hazmat.primitives import hashes

# VERSION: 3.0
versionFloat = "3.0"
print(f"*****|CLIENT VERSION: {versionFloat}|*****")


# ideally these would be setup by arguments or some sort of input system
serverIP = input("Server IP: ") or socket.gethostbyname(socket.gethostname())
serverPort = int(input("Server Port: ") or 5000)
password = input("Server Password: ") # switch input with a hidden input library

hashDigest = hashes.Hash(hashes.SHA256())
hashDigest.update(password.encode())
hashedPassword = base64.urlsafe_b64encode(hashDigest.finalize())


serverAddr = (serverIP, serverPort)
DisconnMsg = '' # we will fill this with the first message the server sends (to keep the disconnect messages the same between versions)
nickname = ''


MyInterface = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    MyInterface.connect(serverAddr)
except:
    print("ERR: server is not on!")
    os._exit(0)

# send threaded
# recieve threaded

# should periodically ping the server so we can tell if it shutdown during chat or not

def send():
    while True:
        try:
            message = input(">").encode()
            if message:
                key = fernet.Fernet(hashedPassword)
                encryptedMessage = key.encrypt(message)
                if message.decode() == DisconnMsg:
                    encryptedDisconn = key.encrypt(DisconnMsg)
                    MyInterface.send(encryptedDisconn)
                    os._exit(0)
                else:
                    MyInterface.send(encryptedMessage)
        except:
            print("The server probably shutdown!")
            os._exit(0)
    
def recieve():
    global DisconnMsg
    key = fernet.Fernet(hashedPassword)
    while True:
        try:
            EncMessage = MyInterface.recv(2048)
            if EncMessage:

                message = key.decrypt(EncMessage).decode()

                if message == "NICK":
                    MyInterface.send(key.encrypt(nickname.encode())) # move this and the input field to its own function in case we need to re query from the server side
                elif message == "ESCAPESEQUENCE":
                    DisconnMsg = key.decrypt(MyInterface.recv(2048)).decode()
                    print(f"\bDisconnect with: \"{DisconnMsg}\"", end="\n>")
                else:
                    print("\b" + message, end="\n>") # delete the little ">" print the message and print a new line with the ">" for user input again
        except:
            pass

nickname = input("Enter a nickname> ") # make user choose a nickname so their IP isn't directly sent to other users

sendThread = threading.Thread(target=send)
sendThread.start()
recieveThread = threading.Thread(target=recieve)
recieveThread.start()