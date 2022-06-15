import sys
import select

from menu import *
from conexoes import *
from erros import *
from inputs import *
import estilo
import threading
import caixa_entrada

usuarioLogado = ""
usuariosAtivos = {}
conexoesAtivas = {}
chatAtivo = False
conexoes = [sys.stdin]
mutex = threading.Lock()
threads = []

def atendeRequisicaoBackground(sock_cliente):
    """Trabalha em background registrando conexoes e mensagens
    que chegam sem o usuário estar com uma conversa aberta"""

    global chatAtivo
    global conexoes

    mutex.acquire()
    conexoes.append(sock_cliente)
    mutex.release()

    while True:
        r, w, x = select.select(conexoes, [], [])
        for request in r:
            if request == sock_cliente: #registra e aceita pedidos de conexao sem conversa aberta
                sock_outro_cliente = aceitarNovaConexao(sock_cliente)
                mutex.acquire()
                conexoes.append(sock_outro_cliente)
                mutex.release()

            elif request != sys.stdin:
                mutex.acquire()
                if not chatAtivo: #caso em que o usuario nao abriu nenhuma conversa
                    processarMensagem(request, conexoes) #a mensagem eh salva para que ele leia depois
                mutex.release()



def processarMensagem(request,conexoes):
    """Recebe e registra na caixa de entrada as mensagens que chegam,
    tanto as que chegam enquanto o usuário está com a conversa aberta
    quanto as que chegam quando está com a conversa fechada"""
    global conexoesAtivas

    data = recebeMensagem(request)

    if not data:
        encerrarConversa(request,conexoes)
        return

    caixa_entrada.registrarMensagem(data["username"], data, False)

    #registra a conversa em andamento com um dado usuario
    # atraves do seu nome e do socket que usará para responder essa mensagem
    conexoesAtivas[data["username"]] = request

def encerrarConversa(request,conexoes):
    """Finaliza conversas em andamento, usamos para mensagens que
    chegam vazia, ou seja, quando o outro usuario se desconecta"""
    conexoes.remove(request)
    request.close()

def mostrarUsuariosAtivos():
    """Mostra os usuários registrados no servidor central"""
    global usuariosAtivos
    usuariosAtivos = get_lista(usuarioLogado)

    #trata casos de nenhum usuario estar registrado
    if naoHaUsuariosDisponiveis(usuariosAtivos):
        return

    #mostra lista enumerada com usuarios ativos
    print(MSG_USUARIOS_ATIVOS)
    usernames = usuariosAtivos.keys()
    print('\n'.join('\t{}: {}'.format(*k) for k in enumerate(usernames)))
    print('\n')

def mostrarConversasAtivas():
    """Mostra conversas em andamento juntamente com notificacao
    de novas mensagens não lidas"""

    if len(conexoesAtivas) == 0:
        return

    print(MSG_CONVERSAS_ATIVAS)
    print('\n'.join('\t{}: {}'.format(*k) for k in enumerate(caixa_entrada.atualizarNotificacoes(conexoesAtivas))))
    print('\n')


def escolherDestinatario():
    """Requisita escolha de destinatário para que o usuário
    inicie ou continue uma conversa"""

    mostrarUsuariosAtivos()

    #verificação para quando não há usuários registrados no servidpr
    if naoHaUsuariosDisponiveis(usuariosAtivos):
        return

    usuarioEscolhido = input(MSG_DESTINATARIO)

    while usuarioInvalido(usuarioEscolhido, usuariosAtivos):
        #cancela a abertura da conversa
        if usuarioEscolhido == "sair":
            return
        usuarioEscolhido = input(MSG_DESTINATARIO)

    return usuarioEscolhido

def pedeConexao():
    """Inicia conexão com outro cliente, seja para iniciar como para
    continuar uma conversa"""

    # verifica se existe um usuário logado no sistema para entrar no chat
    if usuarioNaoLogado(usuarioLogado):
        return

    #Caso em que nao há outros usuarios no servidor, voltando ao menu
    usuarioEscolhido = escolherDestinatario()
    if usuarioEscolhido is None:
        return None, None

    # tenta recuperar o socket já existente caso já tivesse
    # recebido mensagem desse cliente anteriormente
    if not conexoesAtivas.get(usuarioEscolhido, None):
        enderecoNovoCliente = usuariosAtivos[usuarioEscolhido]["Endereco"]
        portaNovoCliente = usuariosAtivos[usuarioEscolhido]["Porta"]

        envioSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        envioSock.connect((enderecoNovoCliente,portaNovoCliente))

    else:
        envioSock = conexoesAtivas.get(usuarioEscolhido)

    return usuarioEscolhido, envioSock


def abrirConversa(usuario):
    """Mostra as mensagens do usuario escolhido"""
    cls() #limpa a tela para apenas mostrar mensagens

    mutex.acquire()
    print("\n\n")
    mensagens = caixa_entrada.getMensagens()
    estilo.carregarMensagens(mensagens, usuario)
    mutex.release()

    print(MSG_DIGITAR_MENSAGEM)


def fecharConversa():
    """Fecha a conversa que está sendo visualizada, não é o mesmo
    que encerrar a conexão, apenas volta para o menu"""

    mutex.acquire()
    global chatAtivo

    # desativa flag para notificar que agora devera registrar as mensagens em background
    chatAtivo = False
    mutex.release()

    #limpa tela para voltar o menu
    cls()
    estilo.carregarHeader()
    mostrarConversasAtivas()


def digitarNoChat(msg, envioSock, usuario):
    """Recebe a mensagem digitada pelo usuario, envia ao
    destinatario e registra na caixa de entrada"""

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
    global conexoesAtivas
    global conexoes

    cls()

    mutex.acquire()

    #notifica o programa de que agora devera registra mensagens chegadas em foreground
    chatAtivo = True
    if envioSock not in conexoes:
        conexoes.append(envioSock)

    #remove notificação de mensagem para registrar como lida
    caixa_entrada.removeNotificacao(destinatario)
    mutex.release()

    while True:
        #mostra mensagens do usuario selecionado
        abrirConversa(destinatario)

        r, w, x = select.select(conexoes, [], [])
        for request in r:
            # caso algum cliente tente se conectar enquanto o usuario esta vendo as mensagens, se houver
            # pode ser o destinario ou outro cliente
            if request == recebeSock:
                sock_outro_cliente = aceitarNovaConexao(recebeSock)
                mutex.acquire()
                conexoes.append(sock_outro_cliente)
                mutex.release()

            # usuario envia mensagem para o destinatario
            elif request == sys.stdin:
                msg = input()

                if msg == 'fim':
                    fecharConversa()
                    return
                digitarNoChat(msg, envioSock, destinatario)

            else:
                #usuario recebe mensagem do usuario que esta conversando ou de outro
                data = recebeMensagem(request)

                if not data:
                    mutex.acquire()
                    encerrarConversa(request, conexoes)

                    usuarios = get_lista(usuarioLogado)
                    envioSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                    envioSock.connect((usuarios[destinatario]["Endereco"], usuarios[destinatario]["Porta"]))
                    conexoesAtivas[destinatario] = envioSock
                    mutex.release()
                else:
                    mutex.acquire()

                    #verifica se a mensagem é do usuario com quem está conversando
                    visualizada = data["username"] == destinatario
                    caixa_entrada.registrarMensagem(data["username"], data, visualizada)
                    mutex.release()


def main():
    '''Funcao principal do cliente'''
    global usuarioLogado

    estilo.carregarHeader()

    # inicia o cliente para escutar
    sock_cliente, porta = prepararClienteParaEscuta()

    # thread que fica escutando chegada de mensagens
    # e pedidos de conexao fora de um chat aberto
    novaConversa = threading.Thread(target=atendeRequisicaoBackground, args=(sock_cliente,))
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
            # mostra usuarios conectados ao servidor
            mostrarUsuariosAtivos()

        elif cmd == 'chat':
            # mostra as conversas em andamente com outros usuarios
            mostrarConversasAtivas()

            # requisita conexao com destinatario
            usuarioEscolhido, envioSock = pedeConexao()
            if usuarioEscolhido is None:
                continue

            # abre chat para conversa
            iniciaChat(envioSock, sock_cliente, usuarioEscolhido)

        elif cmd == 'sair':
            # encerra o programa
            sock_cliente.close()
            exit(0)
        else:
            comandoInvalido(cmd)

main()
