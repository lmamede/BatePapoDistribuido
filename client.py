# servidor de echo: lado cliente
import socket
import json
import select
import sys
import threading

CENTRAL_SERVER = 'localhost'
CENTRAL_SERVER_PORT = 5001

HOST = ''
PORT = 5002
inputs = [sys.stdin]

connections = {}
threads = []
usuarioLogado = ""


username = ''

def iniciaCliente():
    '''Cria um socket de servidor para 
    atender as requisicoes de conversa
    dos outros clientes.
    Saida: socket criado'''

    # cria socket
    # Internet (IPv4 + TCP)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.bind((HOST, PORT))

    sock.listen(5)

    sock.setblocking(False)

    inputs.append(sock)

    return sock


def connectWithCentralServer():
    # Internet (IPv4 + TCP)
    newSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    newSock.connect((CENTRAL_SERVER, CENTRAL_SERVER_PORT))

    return newSock


def login():
    global usuarioLogado

    if (usuarioLogado != ""):
        print("Você já está logado como:", usuarioLogado)
        return

    serverSock = connectWithCentralServer()

    while (True):
        username = input("Escolha um username: ('fim' para terminar):")

        if (username == ""):
            print("Nome de usuário não pode ser vazio.")
            continue

        # envia a mensagem do usuario para o servidor
        mensagem = {"operacao": "login", "username": username, "porta": PORT}
        enviaMensagem(mensagem, serverSock)

        resposta = recebeMensagem(serverSock)

        print(resposta["mensagem"])

        if (resposta["status"] == 200):
            usuarioLogado = username
            break

def get_lista():
    server_sock = connectWithCentralServer()

    mensagem = {"operacao": "get_lista"}
    mensagem_json = json.dumps(mensagem)
    server_sock.send(mensagem_json.encode("utf-8"))

    resposta = server_sock.recv(1024)
    resposta = json.loads(resposta.decode("utf-8"))

    clientes = resposta["clientes"]

    print(clientes)

def logoff():
    serverSock = connectWithCentralServer()
    
    global username
    mensagem = {"operacao":"logoff", "username":username}
    mensagemJson = json.dumps(mensagem)
    serverSock.send(mensagemJson.encode("utf-8"))

# aceita um pedido de conexão e realiza seu tratamento
def aceitaConexao(sock):

    novoSock, endr = sock.accept() # aceita o pedido de conexão
    connections[novoSock] = endr # adiciona a nova conexão ao registro de conexões
    return novoSock, endr
    '''
    # faz a validação
    # pede a lista de usuários logados no servidor central
    usuarios = get_lista()
    # percorre os usuários conectados ao servidor central, procurando pelo endereço que está pedindo conexão
    for username in usuarios:
        if(usuarios[username]["endereco"] == endr):
            # retorna o novo socket e seu endereço, caso conste na lista de usuários ativos
            connections[novoSock] = endr
            return novoSock, endr
        else:
            continue
    # caso o endereço não conste na lista retorna um erro
    print(f"Alerta: o endereço {endr} está realizando uma tentativa de bypass no servidor central!!!")
    '''

# atende a requisição de uma de suas conexões
def atendeRequisicao(clientSock, endr):
    while(True):
        data = clientSock.recv(1024)
        if not data:
            print(str(endr) + '-> encerrou')
            clientSock.close()
            return
        else:
            #  exibe mensagem
            print(str(endr) + ': ' + str(data, encoding='utf-8'))

# faz um pedido de conexão com outro cliente
def pedeConexao():
    '''
    # pede ao servidor a lista de todos os usuários ativos
    usuarios = get_lista()
    # flag de controle para determinar se o usuário escolhido para realizar a conversa é válido ou não
    usuarioValido = False
    if(len(usuarios) == 0):
        print("Nenhum usuário disponível para conversa.")
    else:
        print(f"Estes são os usuários que estão disponíveis para uma conversa: {str([username for username in usuarios])[1:-1]}.")
        usuarioEscolhido = input("digite o nome do usuário com quem você deseja conversar: ")
        while(usuarioValido == False):
            if(usuarioEscolhido not in usuarios):
                print("Este usuário não é valido.")
                usuarios = get_lista()
                if(len(usuarios) == 0):
                    print("Nenhum usuário disponível para conversa.")
                    break;
                else:
                    print(f"Estes são os usuários que estão disponíveis para uma conversa: {str([username for username in usuarios])[1:-1]}.")
                    usuarioEscolhido = input("digite o nome do usuário com quem você deseja conversar: ")
            else:
                usuarioValido = True
        sock.connect((usuarios[usuarioEscolhido]["endereco"], usuarios[usuarioEscolhido]["porta"]))
        return sock
    '''

def enviaMensagem(mensagem, sock):
    mensagemJson = json.dumps(mensagem)
    tamanho = len(mensagemJson)
    mensagemComTamanho = str(tamanho) + mensagemJson
    sock.sendall(mensagemComTamanho.encode("utf-8"))


def recebeMensagem(sock):
    tamanho = int.from_bytes(sock.recv(2), byteorder="big")
    mensagem = sock.recv(tamanho)

    return json.loads(mensagem.decode("utf-8"))


def main():
    '''Funcao principal do cliente'''
    # inicia o cliente
    sock = iniciaCliente()
    print("Pronto para receber conexoes...")
    while True:
        print('flag1')
        r, w, x = select.select(inputs, [], [])
        print('flag2')
        for request in r:
            print('flag3')
            if request == sock:  # Caio
                print('chamada sock')
                # outro cliente iniciando conversa
                # servidor respondendo ou cliente conversando
                novoSock, endr = aceitaConexao(sock)
                # criar thread
                novaConversa = threading.Thread(target=atendeRequisicao, args=(novoSock, endr))
                novaConversa.start()
                threads.append(novaConversa)

            elif request == sys.stdin:
                print('chamada stdin')
                cmd = input()
                if cmd == 'login':  # Alvaro
                    login()
                elif cmd == 'logoff':  # Rodrigo
                    # remove registro do servidor
                    logoff()
                elif cmd == 'get_lista':  # Lorena
                    # recupera listagem com usuarios ativos
                    get_lista()
                else:
                    # envio de mensagem
                    print(cmd)
                    
            print('flag4')
main()
