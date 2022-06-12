from conexoes import *
import os

usuarioLogado = ""


def login(porta):
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
        mensagem = {"operacao": "login",
                    "username": username, "porta": int(porta)}

        enviaMensagem(mensagem, serverSock)

        resposta = recebeMensagem(serverSock)

        print(resposta["mensagem"])

        if (resposta["status"] == 200):
            usuarioLogado = username
            break

    return usuarioLogado


def get_lista():
    server_sock = connectWithCentralServer()

    mensagem = {"operacao": "get_lista"}
    enviaMensagem(mensagem, server_sock)
    # mensagem_json = json.dumps(mensagem)
    # server_sock.send(mensagem_json.encode("utf-8"))

    # resposta = server_sock.recv(1024)
    # resposta = json.loads(resposta.decode("utf-8"))
    resposta = recebeMensagem(server_sock)
    clientes = resposta["clientes"]
    print(clientes)
    return clientes


def logoff():
    global usuarioLogado

    if (usuarioLogado == ""):
        print("Não existe um usuário logado.")
        return

    serverSock = connectWithCentralServer()

    mensagem = {"operacao": "logoff", "username": usuarioLogado}

    enviaMensagem(mensagem, serverSock)

    resposta = recebeMensagem(serverSock)

    print(resposta["mensagem"])

    if (resposta["status"] == 200):
        usuarioLogado = ""

    return usuarioLogado


def cls():
    os.system('cls' if os.name == 'nt' else 'clear')
