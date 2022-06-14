

def carregarHeader():
    with open('header.txt', 'r') as f:
        print('\x1b[;32;1m' + f.read() + '\x1b[0m')