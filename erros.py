"""Verificações usadas no programa"""

ERRO_JA_LOGADO = "Você já está logado como:"
ERRO_USUARIO_VAZIO = "Nome de usuário não pode ser vazio."
ERRO_NAO_LOGADO = "Você deve realizar o login para utilizar o chat."
ERRO_USUARIO_INVALIDO = "Este usuário não é valido."
ERRO_NAO_HA_USUARIOS_ATIVOS = "Nenhum usuário disponível para conversa."
ERRO_COMANDO_NAO_ENCONTRADO = "Comando não encontrado: "

def usuarioJaLogado(usuarioLogado):
    if usuarioLogado != "":
        print(ERRO_JA_LOGADO, usuarioLogado)
        return True
    return False

def usuarioNaoLogado(usuarioLogado):
    if usuarioLogado == "":
        print(ERRO_NAO_LOGADO, usuarioLogado)
        return True
    return False

def usuarioVazio(username):
    if username == "":
        print(ERRO_USUARIO_VAZIO)

def naoHaUsuariosDisponiveis(usuarios):
    if len(usuarios) == 0:
        print(ERRO_NAO_HA_USUARIOS_ATIVOS)
        return True
    return False

def usuarioInvalido(usuario, usuarios):
    if usuario not in usuarios:
        print(ERRO_USUARIO_INVALIDO)
        return True
    return False

def comandoInvalido(cmd):
    print(ERRO_COMANDO_NAO_ENCONTRADO, cmd)