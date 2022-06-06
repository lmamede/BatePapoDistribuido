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

usuarioLogado = ""


# atende a requisição de uma de suas conexões
def atendeRequisicao(sock):
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
                while(True):
                    data = recebeMensagem(request)
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
                        mutex.release()


# faz um pedido de conexão com outro cliente
def pedeConexao():
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

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        sock.connect((usuarios[usuarioEscolhido]["endereco"],
                      usuarios[usuarioEscolhido]["porta"]))

        iniciaChat(sock, usuarioEscolhido)


def iniciaChat(sock, usuario):
    # le as mensagens do usuario ate ele digitar 'fim'
    while True:
        cls()
        for mensagem in mensagens.get(usuario, []):
            print(f"{mensagem['username']}: {mensagem['mensagem']}")

        msg = input("Digite uma mensagem ('fim' para terminar):")
        if msg == 'fim':
            break

        msg_obj = {"username": usuarioLogado, "mensagem": msg}
        # envia a mensagem do usuario para o servidor
        enviaMensagem(msg_obj, sock)

        mutex.acquire()
        if not mensagens.get(usuario):
            mensagens[usuario] = []
        #  exibe mensagem
        mensagens[usuario].append(msg_obj)
        mutex.release()

    # encerra a conexao
    sock.close()


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
            pedeConexao()
        else:
            # envio de mensagem
            print("Comando não encontrado: ", cmd)


main()
