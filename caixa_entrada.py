import estilo

mensagens = {}
notificacoes = {}

def registrarMensagem(username, msg, visualizada):
    """Registra mensagens recebidas em background ou foreground"""
    global mensagens
    global notificacoes

    if not mensagens.get(username):
        mensagens[username] = []

    mensagens[username].append(msg)

    # se a mensagem for em backgound, ainda nao foi visualizada
    # e uma notificacao é vinculada ao usuario
    if not visualizada:
        if not notificacoes.get(username, None):
            notificacoes[username] = 0
        notificacoes[username] = notificacoes[username] + 1

def getMensagens():
    return mensagens

def atualizarNotificacoes(usuariosEmConversa):
    """Retorna o numero de mensagens nao lidas para os usuarios que estao em conversa com
    o cliente

    Saida: string formatada com a notificaçoes"""
    notificacoesUsuarios = map(lambda x: str(x) + getNotificacoes(x), usuariosEmConversa)
    return notificacoesUsuarios

def getNotificacoes(username):
    """Retorna string com número de notificações formatado"""
    if notificacoes.get(username, None):
        return estilo.carregarNotificacoes(str(notificacoes.get(username)))
    return ""

def removeNotificacao(usuario):
    """Remove notificação de mensagem já visualizada"""
    if notificacoes.get(usuario, None):
        del notificacoes[usuario]
