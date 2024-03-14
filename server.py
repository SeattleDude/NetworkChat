import socket, threading, base64
from cryptography import fernet
from cryptography.hazmat.primitives import hashes

# VERSION: 4.0
versionFloat = "4.0"
print(f"*****|SERVER VERSION: {versionFloat}|*****")

serverIP = socket.gethostbyname(socket.gethostname())
serverPort = 5000 # making this standard is easier than syncing over the network between server and client
serverAddr = (serverIP, serverPort)
DisconnMsg = "ESC!!" # server owner can customize this

# need to implement server side protection for buffer overflow to crash the server with input
bufferSize = 4096 # buffer size for input, can be overflowed and crash the server

password = input("Set a secure password> ") or "password"
digest = hashes.Hash(hashes.SHA256())
digest.update(password.encode())
hashedPassword = base64.urlsafe_b64encode(digest.finalize())


listenInterface = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listenInterface.bind(serverAddr) # setup listening interface for recieving data
listenInterface.listen()

clientList = []
nicknameList = []

# broadcast worker function
# handleClientJoin threaded
# recieve threaded

#TODO: implement a chat history so we can administer the server and send the chat logs to new users so they can get the FULL conversation history
# this may not be a good idea for user trust tho

def EncSend(connection,  message):
    try:
        message = message.encode()
    except:
        pass
    key = fernet.Fernet(hashedPassword)
    encryptedMessage = key.encrypt(message)
    connection.send(encryptedMessage)

# we try not to broadcast the users IP so they can try to stay as anonymous as possible
def broadcast(message, preamble): # sends message to ALL clients in clientList (should be connected)
    if type(message) != bytes():
        message = message.encode()
    for client in clientList:
        try:
            key = fernet.Fernet(hashedPassword)
            encryptedMessage = key.encrypt(message)
            if client == preamble:
                continue
            else:
                client.send(encryptedMessage)
        except:
            # print(client)
            print("broadcastFuncErr!")

def clientMsg(client, address, nickName): # takes client parameter; type = connection object
    key = fernet.Fernet(hashedPassword)
    formattedAddr = f"{address[0]}:{address[1]}"
    alive = True
    while alive:
        try:
            EncMsg = bytes(client.recv(bufferSize)) # try to recieve data
            if EncMsg:

                msg = key.decrypt(EncMsg).decode()

                if msg == DisconnMsg:
                    clientList.remove(client)
                    client.close()
                    try:
                        broadcast(f"{nickName} left!", client) # in fString could be formattedAddr or userNickName
                        print(f"({formattedAddr}--{nickName}) left!")
                    except:
                        print(f"({formattedAddr}--{nickName}) left!")
                    alive = False
                else:
                    broadcast(f"{nickName}: {msg}", client) # in fString could be formattedAddr or userNickName
                    print(f"({formattedAddr}--{nickName}): {msg}")
        except OSError: # handle dirty disconnects from the client (client terminal closed)
            broadcast(f"{nickName} Disconnected!", client)
            print(f"({formattedAddr}--{nickName}) Probable Disconnect!") # we cant be sure if it was an intentional disconnect, in any case, the client is no longer connected
            clientList.remove(client)
            nicknameList.remove(nickName)
            alive = False
            break

def recieve():
    key = fernet.Fernet(hashedPassword)
    while True:
        conn, addr = listenInterface.accept()
        formattedAddr = f"{addr[0]}:{addr[1]}"
        EncSend(conn, 'NICK'.encode())
        # conn.send('NICK'.encode()) # query user for nickname
        # print(conn.recv(bufferSize).decode())
        try:
            userNickName = key.decrypt(conn.recv(bufferSize)).decode()
        except:
            # the password wasn't entered correctly!
            print(f"Failed auth attempt! -> {formattedAddr}")
            continue
        # userNickName = conn.recv(bufferSize).decode()
        EncSend(conn, 'ESCAPESEQUENCE'.encode())
        # conn.send('ESCAPESEQUENCE'.encode()) # sync the userSide disconn message
        EncSend(conn, DisconnMsg.encode())
        # conn.send(DisconnMsg.encode())
        clientList.append(conn)
        nicknameList.append(userNickName)
        broadcast(f"{userNickName} connected!", conn) # in fString could be formattedAddr or userNickName
        # print all the existing connections like a current user list so the user knows who is in the room
        print(f"({formattedAddr}--{userNickName}) connected!")

        handleThread = threading.Thread(target=clientMsg, args=(conn,addr, userNickName))
        handleThread.start()

print(f"server is listening on: {serverIP}:{serverPort}")
# moved the starting method to a thread so later on I can make a server admin UI or terminal input for starting and stopping the server etc...
recieveThread = threading.Thread(target=recieve)
recieveThread.start()