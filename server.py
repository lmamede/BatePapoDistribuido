import socket
import select
import sys
import threading
import json

# define a localizacao do servidor
HOST = ''  # vazio indica que podera receber requisicoes a partir de qq interface de rede da maquina
PORT = 6004  # porta de acesso

# define a lista de I/O de interesse (jah inclui a entrada padrao)
entradas = [sys.stdin]
conexoes = {}
usuarios = {}


def iniciaServidor():
    '''Cria um socket de servidor e o coloca em modo de espera por conexoes
    Saida: o socket criado'''

    # cria o socket
    # Internet( IPv4 + TCP)
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


def enviaMensagem(mensagem, sock):
    mensagemJson = json.dumps(mensagem)
    tamanho = len(mensagemJson.encode('utf-8'))
    tamanho_em_bytes = tamanho.to_bytes(2, byteorder="big")
    sock.sendall(tamanho_em_bytes)
    sock.sendall(mensagemJson.encode("utf-8"))

def recebeMensagem(sock):
    print('recebeMensagem')
    tamanho = int.from_bytes(sock.recv(2), byteorder="big")
    chunks = []
    recebidos = 0
    while recebidos < tamanho:
        chunk = sock.recv(min(tamanho-recebidos, 2048))
        if not chunk:
            pass
        # retorna erro ou gera exce ̧c~ao
        chunks.append(chunk)
        recebidos = recebidos + len(chunk)
    mensagem = b''.join(chunks)
    return json.loads(mensagem.decode("utf-8")) if tamanho > 0 else None

def aceitaConexao(sock):
    '''Aceita o pedido de conexao de um cliente
    Entrada: o socket do servidor
    Saida: o novo socket da conexao e o endereco do cliente'''

    # estabelece conexao com o proximo cliente
    clisock, endr = sock.accept()

    # registra a nova conexao
    conexoes[clisock] = endr

    return clisock, endr


def atendeRequisicoes(clisock, endr):
    print('atendeReq')
    '''Recebe mensagens e as envia de volta para o cliente (ate o cliente finalizar)
    Entrada: socket da conexao e endereco do cliente
    Saida: '''

    while True:
        # recebe dados do cliente
        data = recebeMensagem(clisock)
        print(data)
        if not data:  # dados vazios: cliente encerrou
            print(str(endr) + '-> encerrou')
            clisock.close()  # encerra a conexao com o cliente
            return

        operacao = data["operacao"]

        if operacao == 'login':
            login(data["username"], endr, data["porta"], clisock)
        elif operacao == 'logoff':
            # remove registro do servidor
            if conexoes[clisock] == endr: # verifica se a reqiosocao de logoff veio do proprio cliente
                logoff(data["username"])
        elif operacao == 'get_lista':
            #retorn lista com usuarios ativos
            get_lista(clisock)


def login(username, endr, porta, clisock):
    # TODO: validacao de usuario
    if (username in usuarios):
        mensagem = {"operacao": "login", "status": 400,
                    "mensagem": "Username em Uso"}
        enviaMensagem(mensagem, clisock)
    else:
        usuarios[username] = {"endereco": endr[0], "porta": porta}
        mensagem = {"operacao": "login", "status": 200,
                    "mensagem": "Login com sucesso"}
        enviaMensagem(mensagem, clisock)

def get_lista(client_sock):
    mensagem = {"operacao": "get_lista", "status": "200", "clientes": usuarios}
    enviaMensagem(mensagem, client_sock)
    #mensagem_json = json.dumps(mensagem)
    #client_sock.send(mensagem_json.encode("utf-8"))

def logoff(username):
    del usuarios[username]
    print(f'{username} desconectou-se')

def main():
    '''Inicializa e implementa o loop principal (infinito) do servidor'''
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
