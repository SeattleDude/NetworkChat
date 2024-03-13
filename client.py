import socket, threading, os

# VERSION: 2.0
versionFloat = "2.0"

# ideally these would be setup by arguments or some sort of input system
serverIP = input("Server IP: ") or socket.gethostbyname(socket.gethostname())
serverPort = int(input("Server Port: ") or 5000)

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
                if message.decode() == DisconnMsg:
                    MyInterface.send(DisconnMsg.encode())
                    os._exit(0)
                else:
                    MyInterface.send(message)
        except:
            print("The server probably shutdown!")
            os._exit(0)
    
def recieve():
    global DisconnMsg
    while True:
        try:
            message = MyInterface.recv(2048).decode()
            if message:
                if message == "NICK":
                    MyInterface.send(nickname.encode()) # move this and the input field to its own function in case we need to re query from the server side
                elif message == "ESCAPESEQUENCE":
                    DisconnMsg = MyInterface.recv(2048).decode()
                    print(f"\bDisconnect with: \"{DisconnMsg}\"", end="\n>")
                else:
                    print("\b" + message, end="\n>") # delete the little ">" print the message and print a new line with the ">" for user input again
        except:
            pass

def TellVersion():
    print(f"*****|CLIENT VERSION: {versionFloat}|*****")

TellVersion()
nickname = input("Enter a nickname> ") # make user choose a nickname so their IP isn't directly sent to other users

sendThread = threading.Thread(target=send)
sendThread.start()
recieveThread = threading.Thread(target=recieve)
recieveThread.start()