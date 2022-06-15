
ANSI = '\x1b['
AZUL = ANSI + "1;36;1m"
VERMELHO = ANSI + "1;31;1m"
VERDE = ANSI + "1;32;1m"

ANSI_CLOSE = ANSI + '0m'
HEADER = ANSI + ";32;1m"
NOTIFICACOES = ANSI + ";32;1m"


def carregarHeader():
    with open('header2.txt', 'r') as f:
        print(HEADER + f.read() + ANSI_CLOSE)

def carregarNotificacoes(notificacoes):
    return NOTIFICACOES + ' +' + notificacoes + " mensagens" + ANSI_CLOSE

def carregarMensagens(mensagens, usuario):
    colors = {}
    count = 0
    for mensagem in mensagens.get(usuario, []):
        user = mensagem['username']
        if not colors.get(user, None):
            count = (count + 1) % 2
            if count == 0:
                colors[user] = AZUL
            else:
                colors[user] = VERMELHO

        print(f"{colors.get(user)}{user}:{ANSI_CLOSE} {mensagem['mensagem']}")