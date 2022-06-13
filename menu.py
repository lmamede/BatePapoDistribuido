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

    resposta = recebeMensagem(server_sock)
    clientes = resposta["clientes"]

    print("\nUsuários ativos no momento, escolha um para conversar: ")
    usernames = clientes.keys()
    print('\n'.join('\t{}: {}'.format(*k) for k in enumerate(usernames)))
    print('\n')

    return clientes


def logoff():
    global usuarioLogado

    if (usuarioLogado == ""):
        print("Você já está logado.")
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
