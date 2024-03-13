import socket, threading

# VERSION: 3.0
versionFloat = "3.0"


serverIP = socket.gethostbyname(socket.gethostname())
serverPort = 5000 # making this standard is easier than syncing over the network between server and client
serverAddr = (serverIP, serverPort)
DisconnMsg = "ESC!!" # server owner can customize this


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

# we try not to broadcast the users IP so they can try to stay as anonymous as possible
def broadcast(message, preamble): # sends message to ALL clients in clientList (should be connected)
    if type(message) != bytes():
        message = message.encode()
    for client in clientList:
        try:
            if client == preamble:
                continue
            else:
                client.send(message)
        except:
            print(client)

def clientMsg(client, address, nickName): # takes client parameter; type = connection object
    formattedAddr = f"{address[0]}:{address[1]}"
    alive = True
    while alive:
        try:
            msg = bytes(client.recv(2048)).decode() # try to recieve data
            if msg:
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
            print(f"{address[0]}:{address[1]} Probable Disconnect!")
            clientList.remove(client)
            nicknameList.remove(nickName)
            alive = False
            break

def recieve():
    while True:
        conn, addr = listenInterface.accept()
        conn.send('NICK'.encode()) # query user for nickname
        userNickName = conn.recv(2048).decode()
        conn.send('ESCAPESEQUENCE'.encode()) # sync the userSide disconn message
        conn.send(DisconnMsg.encode())
        clientList.append(conn)
        nicknameList.append(userNickName)
        formattedAddr = f"{addr[0]}:{addr[1]}"
        broadcast(f"{userNickName} connected!", conn) # in fString could be formattedAddr or userNickName
        # print all the existing connections like a current user list so the user knows who is in the room
        print(f"({formattedAddr}--{userNickName}) connected!")

        handleThread = threading.Thread(target=clientMsg, args=(conn,addr, userNickName))
        handleThread.start()

def tellVersion():
    print(f"*****|SERVER VERSION: {versionFloat}|*****")

tellVersion()
print(f"server is listening on: {serverIP}:{serverPort}")
recieve()