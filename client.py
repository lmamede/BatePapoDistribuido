# servidor de echo: lado cliente
import socket
import select
import sys
import threading
import time
from menu import *
from conexoes import *


inputs = [sys.stdin]

threads = []

mutex = threading.Lock()

mensagens = {}

conexoesAtivas = {}

chatAtivo = False

usuarioLogado = ""

notificacoes = []


# atende a requisição de uma de suas conexões
def atendeRequisicao(sock):
    global chatAtivo

    conexoes = [sock]

    while True:
        r, w, x = select.select(conexoes, [], [])
        for request in r:
            if request == sock:
                novoSock, _ = aceitaConexao(sock)
                conexoes.append(novoSock)
            else:
                # enquanto a conexão estiver ativa

                mutex.acquire()
                if(not chatAtivo):
                    mutex.release()
                    data = recebeMensagem(request)
                    mutex.acquire()
                    if chatAtivo:
                        break
                    mutex.release()
                    if not data:
                        print(data['username'], '-> encerrou')
                        novoSock.close()
                        return
                    else:

                        mutex.acquire()
                        if not mensagens.get(data["username"]):
                            mensagens[data["username"]] = []
                        #  exibe mensagem
                        mensagens[data["username"]].append(data)
                        conexoesAtivas[data["username"]] = request
                        notificacoes.append(f"Você acabou de receber uma mensagem de {data['username']}")
                        mutex.release()
                    mutex.acquire()
                mutex.release()


# faz um pedido de conexão com outro cliente
def pedeConexao(recebeSock):
    print(f"printando o usuario logado: {usuarioLogado}")
    # verifica se existe um usuário logado no sistema para entrar no chat
    if(usuarioLogado == ""):
        print("Você deve realizar o login para utilizar o chat.")
    else:
        # pede ao servidor a lista de todos os usuários ativos
        usuarios = get_lista()
        print(usuarioLogado)
        usuarios.pop(usuarioLogado)

        # flag de controle para determinar se o usuário escolhido para realizar a conversa é válido ou não
        usuarioValido = False

        if(len(usuarios) == 0):
            print("Nenhum usuário disponível para conversa.")
            return -1
        else:
            print(
                f"Estes são os usuários que estão disponíveis para uma conversa: {str([username for username in usuarios])[1:-1]}.")

            usuarioEscolhido = input(
                "digite o nome do usuário com quem você deseja conversar: ")

            while(usuarioValido == False):
                if(usuarioEscolhido not in usuarios):
                    print("Este usuário não é valido.")
                    usuarios = get_lista()
                    usuarios.pop(usuarioLogado)

                    if(len(usuarios) == 0):
                        print("Nenhum usuário disponível para conversa.")
                        break
                    else:
                        print(
                            f"Estes são os usuários que estão disponíveis para uma conversa: {str([username for username in usuarios])[1:-1]}.")
                        usuarioEscolhido = input(
                            "digite o nome do usuário com quem você deseja conversar: ")
                else:
                    usuarioValido = True

            envioSock = None

            if (not conexoesAtivas.get(usuarioEscolhido, None)):
                envioSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                envioSock.connect((usuarios[usuarioEscolhido]["endereco"],
                                usuarios[usuarioEscolhido]["porta"]))
                print("criei nova conexão")
            else:
                envioSock = conexoesAtivas.get(usuarioEscolhido)
                print("já tem uma conexão ativa")

            iniciaChat(envioSock, recebeSock, usuarioEscolhido)


def iniciaChat(envioSock, recebeSock, usuario):
    # le as mensagens do usuario ate ele digitar 'fim'
    global chatAtivo

    mutex.acquire()
    chatAtivo = True
    mutex.release()
    conexoes = [sys.stdin, recebeSock, envioSock]

    while True:
        if(len(notificacoes) > 0):
            while(len(notificacoes) > 0):
                print(notificacoes.pop(0))
        else:
            print("\n\n")
            for mensagem in mensagens.get(usuario, []):
                print(f"{mensagem['username']}: {mensagem['mensagem']}")

            print("Digite uma mensagem ('fim' para terminar):")

            r, w, x = select.select(conexoes, [], [])
            for request in r:
                if request == recebeSock:
                    novoSock, _ = aceitaConexao(recebeSock)
                    conexoes.append(novoSock)
                    print("recebi novo pedido conexão")
                elif request == sys.stdin:
                    msg = input()
                    if msg == 'fim':
                        mutex.acquire()
                        chatAtivo = False
                        mutex.release()
                        return

                    msg_obj = {"username": usuarioLogado, "mensagem": msg}
                    # envia a mensagem do usuario para o servidor
                    enviaMensagem(msg_obj, envioSock)

                    mutex.acquire()
                    if not mensagens.get(usuario):
                        mensagens[usuario] = []
                    #  exibe mensagem
                    mensagens[usuario].append(msg_obj)
                    mutex.release()
                else:
                    data = recebeMensagem(request)
                    if not data:
                        print(data['username'], '-> encerrou')
                        request.close()
                        return
                    else:
                        mutex.acquire()
                        if not mensagens.get(data["username"]):
                            mensagens[data["username"]] = []
                        #  exibe mensagem
                        mensagens[data["username"]].append(data)
                        notificacoes.append(f"Você acabou de receber uma mensagem de {data['username']}")
                        mutex.release()


def main():
    global usuarioLogado
    '''Funcao principal do cliente'''

    with open('header.txt', 'r') as f:
        print('\x1b[;32;1m' + f.read() + '\x1b[0m')

    # inicia o cliente
    porta = int(input('Digite a porta: '))
    sock = iniciaCliente(porta)

    novaConversa = threading.Thread(
        target=atendeRequisicao, args=(sock,))
    novaConversa.start()
    threads.append(novaConversa)

    while True:
        if(len(notificacoes) > 0):
            while(len(notificacoes) > 0):
                print(notificacoes.pop(0))
        else:
            cmd = input("Digite um comando: ")
            if cmd == 'login':
                # registra o usuário no servidor
                usuarioLogado = login(porta)
            elif cmd == 'logoff':
                # remove registro do servidor
                usuarioLogado = logoff()
            elif cmd == 'get_lista':
                # recupera listagem com usuarios ativos
                get_lista()
            elif cmd == 'chat':
                pedeConexao(sock)
            else:
                # envio de mensagem
                print("Comando não encontrado: ", cmd)


main()
