import socket

IP  = '0.0.0.0'
PORT = 8000

bufferSize = 200000

UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind to address and ip
UDPServerSocket.bind((IP, PORT))


print("UDP server up and listening")

dc = {}
dc[b"version"] = b"Shreyansh's Version"

# Listen for incoming datagrams
while(True):
    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)

    message = bytesAddressPair[0]

    address = bytesAddressPair[1]

    clientMsg = message
    clientIP  = "Client IP Address:{}".format(address)
    
    print(clientMsg)
    print(clientIP)

    # Insert
    if b'=' in clientMsg:
        x, y = clientMsg.split(b'=', 1)
        if x == b'version':
            continue
        else:
            dc[x] = y

    # Retrieve
    else:
        val = dc.get(clientMsg, b'')
        return_val = clientMsg + b'=' + val
        UDPServerSocket.sendto(return_val, address)