import socket
import json

CENTRAL_SERVER = 'localhost'
CENTRAL_SERVER_PORT = 6004

HOST = ''


def iniciaCliente(porta):
    '''Cria um socket de servidor para 
    atender as requisicoes de conversa
    dos outros clientes.
    Saida: socket criado'''

    # cria socket
    # Internet (IPv4 + TCP)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.bind((HOST, int(porta)))

    sock.listen(5)

    # sock.setblocking(False)

    # inputs.append(sock)

    return sock


# aceita um pedido de conexão e realiza seu tratamento
def aceitaConexao(sock):

    novoSock, endr = sock.accept()  # aceita o pedido de conexão
    # adiciona a nova conexão ao registro de conexões
    # connections[novoSock] = endr
    return novoSock, endr


def connectWithCentralServer():
    # Internet (IPv4 + TCP)
    newSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    newSock.connect((CENTRAL_SERVER, CENTRAL_SERVER_PORT))

    return newSock

# envia uma mensagem, onde os dois primeiros bytes representam o tamanho da mensagem


def enviaMensagem(mensagem, sock):
    mensagemJson = json.dumps(mensagem)
    tamanho = len(mensagemJson.encode('utf-8'))
    tamanho_em_bytes = tamanho.to_bytes(2, byteorder="big")
    sock.sendall(tamanho_em_bytes)
    sock.sendall(mensagemJson.encode("utf-8"))


def recebeMensagem(sock):
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
    if(not mensagem):
        return None
    return json.loads(mensagem.decode("utf-8"))
