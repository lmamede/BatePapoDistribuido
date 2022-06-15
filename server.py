import select
import sys
import threading

from conexoes import *

# define a localizacao do servidor
HOST = ''  # vazio indica que podera receber requisicoes a partir de qq interface de rede da maquina
PORT = 6004  # porta de acesso

# define a lista de I/O de interesse (jah inclui a entrada padrao)
entradas = [sys.stdin]
conexoes = {}
usuarios = {}

#campos json
OPERACAO = "operacao"
PORTA_MIN = "porta"
PORTA_MAI = "Porta"
ENDERECO_MIN = "endereco"
ENDERECO_MAI = "Endereco"
MENSAGEM = "mensagem"
STATUS = "status"
USERNAME = "username"
CLIENTES = "clientes"

#operacoes
LOGIN = "login"
LOGOFF = "logoff"
GET_LISTA = "get_lista"

#mensagens
LOGIN_SUCESSO = "Login com sucesso"
LOGIN_INVALIDO = "Username em Uso"
LOGOFF_SUCESSO = "Logoff com sucesso"
LOGOFF_ERRO = "Erro no Logoff"

def iniciaServidor():
    """Cria um socket de servidor e o coloca em modo de espera por conexoes
    Saida: o socket criado"""

    # cria o socket com protocolo TCP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # vincula a localizacao do servidor
    sock.bind((HOST, PORT))

    # coloca-se em modo de espera por conexoes
    sock.listen(5)

    # configura o socket para o modo nao-bloqueante
    sock.setblocking(False)

    # inclui o socket principal na lista de entradas de interesse
    entradas.append(sock)

    return sock


def aceitaConexao(sock):
    """Aceita o pedido de conexao de um cliente
    Entrada: o socket do servidor
    Saida: o novo socket da conexao e o endereco do cliente"""

    # estabelece conexao com o proximo cliente
    clisock, endr = sock.accept()

    # registra a nova conexao
    conexoes[clisock] = endr

    return clisock, endr


def atendeRequisicoes(clisock, endr):
    """Recebe mensagens e as envia de volta para o cliente (ate o cliente finalizar)
    Entrada: socket da conexao e endereco do cliente"""

    while True:
        # recebe dados do cliente
        data = recebeMensagem(clisock)
        print(data)
        if not data:  # dados vazios: cliente encerrou
            print(str(endr) + '-> encerrou')
            clisock.close()  # encerra a conexao com o cliente
            return

        operacao = data[OPERACAO]

        if operacao == LOGIN:
            login(data[USERNAME], endr, data[PORTA_MIN], clisock)
        elif operacao == LOGOFF:
            # remove registro do servidor
            # verifica se a reqiosocao de logoff veio do proprio cliente
            if conexoes[clisock] == endr:
                logoff(data[USERNAME], clisock)
        elif operacao == GET_LISTA:
            # retorn lista com usuarios ativos
            get_lista(clisock)


def login(username, endr, porta, clisock):
    """Registra o usuario na lista do servidor"""
    if (username in usuarios):
        mensagem = {OPERACAO: LOGIN, STATUS: 400,
                    MENSAGEM: LOGIN_INVALIDO}
        enviaMensagem(mensagem, clisock)
    else:
        usuarios[username] = {ENDERECO_MAI: endr[0], PORTA_MAI: porta}
        mensagem = {OPERACAO: LOGIN, STATUS: 200,
                    MENSAGEM: LOGIN_SUCESSO}
        enviaMensagem(mensagem, clisock)


def get_lista(client_sock):
    """Rertorna lista com usuarios ativos"""
    mensagem = {OPERACAO: GET_LISTA, STATUS: 200, CLIENTES: usuarios}
    enviaMensagem(mensagem, client_sock)


def logoff(username, clisock):
    """Remove usuario da lista de usuairos ativos do servidor"""
    if (username not in usuarios):
        mensagem = {OPERACAO: LOGOFF, STATUS: 400,
                    MENSAGEM: LOGOFF_ERRO}
        enviaMensagem(mensagem, clisock)
    else:
        del usuarios[username]
        mensagem = {OPERACAO: LOGOFF, STATUS: 200,
                    MENSAGEM: LOGOFF_SUCESSO}
        enviaMensagem(mensagem, clisock)


def main():
    """Inicializa e implementa o loop principal (infinito) do servidor"""
    clientes = []  # armazena as threads criadas para fazer join
    sock = iniciaServidor()
    print("Pronto para receber conexoes...")
    while True:
        # espera por qualquer entrada de interesse
        leitura, escrita, excecao = select.select(entradas, [], [])
        # tratar todas as entradas prontas
        for pronto in leitura:
            if pronto == sock:  # pedido novo de conexao
                clisock, endr = aceitaConexao(sock)
                print('Conectado com: ', endr)

                # cria nova thread para atender o cliente
                cliente = threading.Thread(
                    target=atendeRequisicoes, args=(clisock, endr))

                cliente.start()
                # armazena a referencia da thread para usar com join()
                clientes.append(cliente)
            elif pronto == sys.stdin:  # entrada padrao
                cmd = input()
                if cmd == 'fim':  # solicitacao de finalizacao do servidor
                    for c in clientes:  # aguarda todas as threads terminarem
                        c.join()
                    sock.close()
                    sys.exit()
                elif cmd == 'hist':  # outro exemplo de comando para o servidor
                    print(str(conexoes.values()))

main()
