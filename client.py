# servidor de echo: lado cliente
import socket
import json
import select
import sys

CENTRAL_SERVER = 'localhost'
CENTRAL_SERVER_PORT = 5000

HOST = ''
PORT = 5001
inputs = [sys.stdin]

connections = {}
threads = []
usuarioLogado = ""


username = ''

def iniciaCliente():
    '''Cria um socket de servidor para 
    atender as requisicoes de conversa
    dos outros clientes.
    Saida: socket criado'''

    # cria socket
    # Internet (IPv4 + TCP)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.bind((HOST, PORT))

    sock.setblocking(False)

    inputs.append(sock)

    return sock


def connectWithCentralServer():
    # Internet (IPv4 + TCP)
    newSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    newSock.connect((CENTRAL_SERVER, CENTRAL_SERVER_PORT))

    return newSock


def login():
    global usuarioLogado

    if (usuarioLogado != ""):
        print("Você já está logado como:", usuarioLogado)
        return

    serverSock = connectWithCentralServer()

    while (True):
        username = input("Escolha um username: ('fim' para terminar):")

        if (username == ""):
            print("Nome de usuário não pode ser vazio.")
            continue

        # envia a mensagem do usuario para o servidor
        mensagem = {"operacao": "login", "username": username, "porta": PORT}
        mensagemJson = json.dumps(mensagem)
        serverSock.sendall(mensagemJson.encode("utf-8"))

        resposta = serverSock.recv(1024)
        resposta = json.loads(resposta.decode("utf-8"))

        print(resposta["mensagem"])

        if (resposta["status"] == 200):
            usuarioLogado = username
            break

def logoff():
    serverSock = connectWithCentralServer()
    
    global username
    mensagem = {"operacao":"logoff", "username":username}
    mensagemJson = json.dumps(mensagem)
    serverSock.send(mensagemJson.encode("utf-8"))

def main():
    '''Funcao principal do cliente'''
    # inicia o cliente
    sock = iniciaCliente()
    while True:
        r, w, x = select.select(inputs, [], [])
        for request in r:
            if request == sock:  # Caio
                # outro cliente iniciando conversa
                # servidor respondendo ou cliente conversando
                # criar thread
                pass

            elif request == sys.stdin:
                cmd = input()
                if cmd == 'login':  # Alvaro
                    login()
                elif cmd == 'logoff':  # Rodrigo
                    # remove registro do servidor
                    logoff()
                elif cmd == 'get_lista':  # Lorena
                    # recupera listagem com usuarios ativos
                    pass
                else:
                    # envio de mensagem
                    print(cmd)


main()
