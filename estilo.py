
ANSI = '\x1b['
ANSI_CLOSE = ANSI + '0m'
HEADER = ANSI + ";32;1m"
NOTIFICACOES = ANSI + ";32;1m"

def carregarHeader():
    with open('header.txt', 'r') as f:
        print(HEADER + f.read() + ANSI_CLOSE)

def carregarNotificacoes(notificacoes):
    return NOTIFICACOES + ' +' + notificacoes + " mensagens" + ANSI_CLOSE