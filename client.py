# servidor de echo: lado cliente
import socket

import sys
import select

from menu import *
from conexoes import *
from estilo import *
from erros import *
from inputs import *
import caixa_entrada

usuarioLogado = ""
usuariosAtivos = {}
conexoesAtivas = {}
chatAtivo = False

# atende a requisição de uma de suas conexões
def atendeRequisicao(sock_cliente):
    global chatAtivo
    conexoes = [sock_cliente]

    while True:
        r, w, x = select.select(conexoes, [], [])
        for request in r:
            if request == sock_cliente:
                sock_outro_cliente = aceitarNovaConexao(sock_cliente)
                conexoes.append(sock_outro_cliente)
            elif request != sys.stdin:
                mutex.acquire()
                if not chatAtivo: #caso em que o usuario nao abriu nenhuma conversa
                    processarMensagem(request)
                mutex.release()



def processarMensagem(request):
    data = recebeMensagem(request)

    if not data:
        encerrarConversa(request)
        return

    caixa_entrada.registrarMensagem(data["username"], data, False)

    conexoesAtivas[data["username"]] = request

def encerrarConversa(request):
    conexoes.remove(request)
    request.close()

def mostrarUsuariosAtivos():
    global usuariosAtivos
    usuariosAtivos = get_lista(usuarioLogado)

    if naoHaUsuariosDisponiveis(usuariosAtivos):
        return

    print("\nUsuários ativos no momento, escolha um para conversar: ")
    usernames = usuariosAtivos.keys()
    print('\n'.join('\t{}: {}'.format(*k) for k in enumerate(usernames)))
    print('\n')

def mostrarConversasAtivas():
    """Mostra conversas em andamento juntamente com novas mensagens não lidas"""

    if len(conexoesAtivas) == 0:
        return

    print("\nVocê está conversando com: ")
    print('\n'.join('\t{}: {}'.format(*k) for k in enumerate(caixa_entrada.atualizarNotificacoes(conexoesAtivas))))
    print('\n')


def escolherDestinatario():
    mostrarUsuariosAtivos()
    if naoHaUsuariosDisponiveis(usuariosAtivos):
        return

    usuarioEscolhido = input(MSG_DESTINATARIO)

    while usuarioInvalido(usuarioEscolhido, usuariosAtivos):
        usuarioEscolhido = input(MSG_DESTINATARIO)

    return usuarioEscolhido

def pedeConexao():
    """Inicia conexão com outro cliente"""

    # verifica se existe um usuário logado no sistema para entrar no chat
    if usuarioNaoLogado(usuarioLogado):
        return

    usuarioEscolhido = escolherDestinatario()
    if usuarioEscolhido is None:
        return None, None

    #tenta recuperar o socket já existente caso já tivesse uma conexao com este cliente
    if not conexoesAtivas.get(usuarioEscolhido, None):
        enderecoNovoCliente = usuariosAtivos[usuarioEscolhido]["Endereco"]
        portaNovoCliente = usuariosAtivos[usuarioEscolhido]["Porta"]

        envioSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        envioSock.connect((enderecoNovoCliente,portaNovoCliente))

    else:
        envioSock = conexoesAtivas.get(usuarioEscolhido)

    return usuarioEscolhido, envioSock


def abrirConversa(usuario):
    cls()
    mutex.acquire()
    print("\n\n")
    mensagens = caixa_entrada.getMensagens()
    for mensagem in mensagens.get(usuario, []):
        print(f"{mensagem['username']}: {mensagem['mensagem']}")
    mutex.release()
    print("Digite uma mensagem ('fim' para terminar): ")


def fecharConversa():
    mutex.acquire()
    global chatAtivo
    chatAtivo = False
    mutex.release()
    cls()


def digitarNoChat(msg, envioSock, usuario):
    msg_obj = {"username": usuarioLogado, "mensagem": msg}
    enviaMensagem(msg_obj, envioSock)
    mutex.acquire()
    caixa_entrada.registrarMensagem(usuario, msg_obj, True)
    mutex.release()


def iniciaChat(envioSock, recebeSock, destinatario):
    """Representa a conversa corrente do usuario com outro,
    a tela do programa passa a só mostrar esta conversa até
    que o usuário digita fim para voltar ao menu"""

    global chatAtivo
    global conexoes
    global conexoesAtivas

    cls()

    mutex.acquire()
    chatAtivo = True
    conexoes = [sys.stdin, envioSock, recebeSock]
    mutex.release()

    while True:
        abrirConversa(destinatario)

        r, w, x = select.select(conexoes, [], [])
        for request in r:
            if request == recebeSock:
                sock_outro_cliente = aceitarNovaConexao(recebeSock)
                conexoes.append(sock_outro_cliente)

            elif request == sys.stdin:
                msg = input()

                if msg == 'fim':
                    fecharConversa()
                    return
                digitarNoChat(msg, envioSock, destinatario)

            else:
                data = recebeMensagem(request)
                if not data:
                    mutex.acquire()
                    conexoes.remove(request)
                    mutex.release()
                    request.close()

                    usuarios = get_lista(usuarioLogado)
                    envioSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                    envioSock.connect((usuarios[destinatario]["Endereco"], usuarios[destinatario]["Porta"]))
                    conexoesAtivas[destinatario] = envioSock
                else:
                    mutex.acquire()
                    caixa_entrada.registrarMensagem(data["username"], data, True)
                    mutex.release()


def main():
    '''Funcao principal do cliente'''
    global usuarioLogado

    carregarHeader()

    # inicia o cliente
    sock_cliente, porta = prepararClienteParaEscuta()

    novaConversa = threading.Thread(target=atendeRequisicao, args=(sock_cliente,))
    novaConversa.start()
    threads.append(novaConversa)

    while True:
        cmd = input("Digite um comando: ")
        if cmd == 'login':
            # registra o usuário no servidor
            usuarioLogado = login(porta)

        elif cmd == 'logoff':
            # remove registro do servidor
            usuarioLogado = logoff()

        elif cmd == 'get_lista':
            mostrarUsuariosAtivos()

        elif cmd == 'chat':
            mostrarConversasAtivas()
            usuarioEscolhido, envioSock = pedeConexao()
            if usuarioEscolhido is None:
                continue
            iniciaChat(envioSock, sock_cliente, usuarioEscolhido)

        elif cmd == 'sair':
            sock_cliente.close()
            exit(0)
        else:
            print("Comando não encontrado: ", cmd)

main()
