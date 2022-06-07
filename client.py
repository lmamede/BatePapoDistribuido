# servidor de echo: lado cliente
import socket
import select
import sys
import threading

from menu import *
from conexoes import *


inputs = [sys.stdin]

threads = []

mutex = threading.Lock()

mensagens = {}

conexoesAtivas = {}

chatAtivo = False

usuarioLogado = ""


# atende a requisição de uma de suas conexões
def atendeRequisicao(sock):
    global chatAtivo

    print('fui chamadoooooo')
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
                    print("recebi mensagem pela thread")
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
                        mutex.release()

                    print("processei mensagem pela thread")
                    mutex.acquire()
                mutex.release()


# faz um pedido de conexão com outro cliente
def pedeConexao(recebeSock):
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
                print("recebi mensagem pelo chat")
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
                    mutex.release()
                print("processei mensagem pelo chat")


def main():
    global usuarioLogado
    '''Funcao principal do cliente'''
    # inicia o cliente
    porta = int(input('Digite a porta: '))
    sock = iniciaCliente(porta)

    novaConversa = threading.Thread(
        target=atendeRequisicao, args=(sock,))
    novaConversa.start()
    threads.append(novaConversa)

    print("Pronto para receber conexoes...\n")
    while True:
        cmd = input("Digite um comando: ")
        if cmd == 'login':  # Alvaro
            usuarioLogado = login(porta)
        elif cmd == 'logoff':  # Rodrigo
            # remove registro do servidor
            usuarioLogado = logoff()
        elif cmd == 'get_lista':  # Lorena
            # recupera listagem com usuarios ativos
            get_lista()
        elif cmd == 'chat':
            print('recebi um comando de chat')
            pedeConexao(sock)
        else:
            # envio de mensagem
            print("Comando não encontrado: ", cmd)


main()
