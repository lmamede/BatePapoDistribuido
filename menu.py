from conexoes import *
from erros import *
import os

usuarioLogado = ""


def login(porta):
    global usuarioLogado

    if usuarioJaLogado(usuarioLogado):
        return

    serverSock = connectWithCentralServer()

    while (True):
        username = input("Escolha um username: ")

        if usuarioVazio(username):
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

    serverSock.close()
    return usuarioLogado


def get_lista(usuarioLogado):
    server_sock = connectWithCentralServer()

    mensagem = {"operacao": "get_lista"}
    enviaMensagem(mensagem, server_sock)

    resposta = recebeMensagem(server_sock)
    clientes = resposta["clientes"]
    clientes.pop(usuarioLogado)

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
