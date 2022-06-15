
mensagens = {}
notificacoes = {}

def registrarMensagem(username, msg, visualizada):
    global mensagens
    global notificacoes

    if not mensagens.get(username):
        mensagens[username] = []

    mensagens[username].append(msg)

    if not visualizada:
        if not notificacoes.get(username, None):
            notificacoes[username] = 0
        notificacoes[username] = notificacoes[username] + 1

def getMensagens():
    return mensagens

def atualizarNotificacoes(usuariosEmConversa):
    notificacoesUsuarios = map(lambda x: str(x) + getNotificacoes(x), usuariosEmConversa)
    return notificacoesUsuarios

def getNotificacoes(username):
    if notificacoes.get(username, None):
        return " +" + str(notificacoes.get(username)) + " mensagens"
    return ""

def removeNotificacao(usuario):
    if notificacoes.get(usuario, None):
        del notificacoes[usuario]
