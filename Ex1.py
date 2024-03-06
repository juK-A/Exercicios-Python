import re

def validar_senha(senha):
    # Verificar se a senha tem pelo menos uma letra maiúscula, uma letra minúscula e um número
    if not re.search(r'[A-Z]', senha) or not re.search(r'[a-z]', senha) or not re.search(r'[0-9]', senha):
        return False
    
    # Verificar se a senha não contém caracteres de pontuação, acentuação ou espaço
    if re.search(r'[^a-zA-Z0-9]', senha):
        return False
    
    # Verificar se a senha tem entre 6 e 32 caracteres
    if len(senha) < 6 or len(senha) > 32:
        return False

    return True

while True:
    try:
        senha = input("Digite a senha (entre 6 e 32 caracteres, contendo pelo menos uma letra maiúscula, uma letra minúscula e um número): ")
        if validar_senha(senha):
            print("Senha válida.")
        else:
            print("Senha inválida.")
    except EOFError:
        break

