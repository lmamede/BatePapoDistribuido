

mensagens = {}

def registrarMensagem(username, msg):
    global mensagens

    if not mensagens.get(username):
        mensagens[username] = []

    mensagens[username].append(msg)

def getMensagens():
    return mensagens