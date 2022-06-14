

ERRO_JA_LOGADO = "Você já está logado como:"
ERRO_USUARIO_VAZIO = "Nome de usuário não pode ser vazio."
ERRO_NAO_LOGADO = "Você deve realizar o login para utilizar o chat."
ERRO_NAO_HA_USUARIOS_ATIVOS = "Nenhum usuário disponível para conversa."

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
        print("Este usuário não é valido.")
        return True
    return False