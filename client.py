#servidor de echo: lado cliente
import socket
import json
import select
import sys

CENTRAL_SERVER='localhost'
CENTRAL_SERVER_PORT = 5000

HOST = ''
PORT = 5001
inputs = [sys.stdin]

connections = {}
threads = []

username = ''

def iniciaCliente():
    '''Cria um socket de servidor para 
    atender as requisicoes de conversa
    dos outros clientes.
    Saida: socket criado'''
    
    # cria socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Internet (IPv4 + TCP) 

    sock.bind((HOST,PORT))

    sock.setblocking(False)

    inputs.append(sock)
    
    return sock

def connectWithCentralServer():
    newSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Internet (IPv4 + TCP) 
    newSock.connect((CENTRAL_SERVER, CENTRAL_SERVER_PORT))
    
    return newSock

def login():
    serverSock = connectWithCentralServer()
    
    msg = input("Escolha um username: ('fim' para terminar):")
    #if msg == 'fim': break 

    global username
    username += msg

    # envia a mensagem do usuario para o servidor
    mensagem = {"operacao":"login", "username":msg, "porta": PORT}
    mensagemJson = json.dumps(mensagem)
    serverSock.send(mensagemJson.encode("utf-8"))

    #TODO: tratar tamanho da mensagem, tratar se usuario ja existe
    #msg = sock.recv(1024) 

    # imprime a mensagem recebida
    #print(str(msg, encoding='utf-8'))

def get_lista():
    server_sock = connectWithCentralServer()

    mensagem = {"operacao": "get_lista"}
    mensagem_json = json.dumps(mensagem)
    server_sock.send(mensagem_json.encode("utf-8"))

    resposta = server_sock.recv(1024)
    resposta = json.loads(resposta.decode("utf-8"))

    clientes = resposta["clientes"]

    print(clientes)

def logoff():
    serverSock = connectWithCentralServer()
    
    global username
    mensagem = {"operacao":"logoff", "username":username}
    mensagemJson = json.dumps(mensagem)
    serverSock.send(mensagemJson.encode("utf-8"))

def main():
    '''Funcao principal do cliente'''
    #inicia o cliente
    sock = iniciaCliente()
    while True:
        r,w,x = select.select(inputs, [], [])
        for request in r:
            if request == sock: #Caio
                #outro cliente iniciando conversa
                #servidor respondendo ou cliente conversando
                #criar thread
                pass

            elif request == sys.stdin:
                cmd = input()
                if cmd == 'login': #Alvaro
                    login()
                elif cmd == 'logoff': #Rodrigo
                    #remove registro do servidor
                    logoff()
                    pass
                elif cmd == 'get_lista':  # Lorena
                    # recupera listagem com usuarios ativos
                    get_lista()
                else:
                    #envio de mensagem
                    print(cmd)

main()
