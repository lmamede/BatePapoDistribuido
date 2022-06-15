import socket
import json
from inputs import *

ENCODE = "utf-8"

CENTRAL_SERVER = 'localhost'
CENTRAL_SERVER_PORT = 6004

HOST = ''

def prepararClienteParaEscuta():
    """Cria um socket de servidor para atender as
    requisicoes de conversa dos outros clientes.

    Saida: socket criado e porta escolhida"""

    porta = int(input(MSG_PORTA))

    # cria socket com protocolo TCP
    sock_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #vincula a porta selecionada pelo usuario
    sock_cliente.bind((HOST, int(porta)))

    #numero de conexoes pendentes
    sock_cliente.listen(5)

    return sock_cliente, porta


def aceitarNovaConexao(sock):
    """Aceita conexao de outro cliente, para iniciar uma conversa"""
    sock_outro_cliente, endr = sock.accept()  # aceita o pedido de conexão

    return sock_outro_cliente

def connectWithCentralServer():
    """Cria um socket de comunicação com o servidor central

    Saida: socket do server"""
    # Internet (IPv4 + TCP)
    newSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    newSock.connect((CENTRAL_SERVER, CENTRAL_SERVER_PORT))

    return newSock

def enviaMensagem(mensagem, sock):
    """Envia uma mensagem, onde os dois primeiros bytes representam o tamanho da mensagem"""
    mensagemJson = json.dumps(mensagem)
    tamanho = len(mensagemJson.encode(ENCODE))
    tamanho_em_bytes = tamanho.to_bytes(2, byteorder="big")
    sock.sendall(tamanho_em_bytes)
    sock.sendall(mensagemJson.encode(ENCODE))


def recebeMensagem(sock):
    """Recebe qualquer mensagem enviada ou pelo servidor central
    ou por outro cliente, resgata até atingir o tamnho notificado

    Saida: mensagem completa em formato JSON"""

    tamanho_mensagem = int.from_bytes(sock.recv(2), byteorder="big")
    chunks = []
    recebidos = 0
    while recebidos < tamanho_mensagem:
        chunk = sock.recv(min(tamanho_mensagem - recebidos, 2048))
        if not chunk:
            pass
        # retorna erro ou gera exce ̧c~ao
        chunks.append(chunk)
        recebidos = recebidos + len(chunk)
    mensagem = b''.join(chunks)
    if(not mensagem):
        return None
    return json.loads(mensagem.decode(ENCODE))
