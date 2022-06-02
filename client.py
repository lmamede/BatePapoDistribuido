# servidor de echo: lado cliente
import socket
import json
import select
import sys

CENTRAL_SERVER = 'localhost'
CENTRAL_SERVER_PORT = 5001

HOST = ''
PORT = 5002
inputs = [sys.stdin]

connections = {}
threads = []
usuarioLogado = ""


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
        enviaMensagem(mensagem, serverSock)

        resposta = recebeMensagem(serverSock)

        print(resposta["mensagem"])

        if (resposta["status"] == 200):
            usuarioLogado = username
            break


def enviaMensagem(mensagem, sock):
    mensagemJson = json.dumps(mensagem)
    tamanho = len(mensagemJson)
    mensagemComTamanho = str(tamanho) + mensagemJson
    sock.sendall(mensagemComTamanho.encode("utf-8"))


def recebeMensagem(sock):
    tamanho = int.from_bytes(sock.recv(2), byteorder="big")
    mensagem = sock.recv(tamanho)

    return json.loads(mensagem.decode("utf-8"))


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
                    pass
                elif cmd == 'get_lista':  # Lorena
                    # recupera listagem com usuarios ativos
                    pass
                else:
                    # envio de mensagem
                    print(cmd)


main()
