def menu_principal():
    menu = """\n
    ====== MENU PRINCIPAL ======
    [d] Depositar
    [s] Sacar
    [e] Extrato
    [u] Criar Usuário
    [c] Criar Conta
    [l] Listar Usuários
    [lc] Listar Contas
    [q] Sair
    =============================
    => """
    return menu

def sacar(*,valor, saldo, limite, numero_saques, extrato, limite_saques):
    if valor > saldo:
        print("Operação falhou! Você não tem saldo suficiente.")
        return saldo, numero_saques, extrato

    if valor > limite:
        print("Operação falhou! O valor do saque excede o limite.")
        return saldo, numero_saques, extrato

    if numero_saques >= limite_saques:
        print("Operação falhou! Número máximo de saques excedido.")
        return saldo, numero_saques, extrato

    saldo -= valor
    numero_saques += 1
    extrato += f"Saque: R$ {valor:.2f}\n"
    return saldo, numero_saques, extrato

def depositar(valor, saldo, extrato):
    if valor <= 0:
        print("Operação falhou! O valor informado é inválido.")
        return saldo, extrato

    saldo += valor
    extrato += f"Depósito: R$ {valor:.2f}\n"
    return saldo, extrato

def exibir_extrato(saldo,/,*,extrato):
    print("\n================ EXTRATO ================")
    print("Não foram realizadas movimentações." if not extrato else extrato)
    print(f"\nSaldo: R$ {saldo:.2f}")
    print("==========================================")

def criar_usuario(usuarios, cpf, nome, data_nascimento, endereco):
    if cpf in usuarios:
        print("Já existe um usuário com esse CPF!")
        return

    usuarios[cpf] = {
        "nome": nome,
        "data_nascimento": data_nascimento,
        "endereco": endereco,
        "cpf": cpf
    }
    print("Usuário criado com sucesso!")

def criar_conta_corrente(agencia, usuarios, cpf, contas):
    if cpf not in usuarios:
        print("Usuário não encontrado, por favor crie um usuário antes de criar uma conta.")
        return

    conta = {
        "agencia": agencia,
        "numero_conta": len(contas)+1,
        "usuario": usuarios[cpf],
    }
    contas.append(conta)
    print("Conta criada com sucesso!")
    return conta

def listar_contas(contas):
    for conta in contas:
        print(f"Agência: {conta['agencia']} | Conta: {conta['numero_conta']} | Usuário: {conta['usuario']}")

def listar_usuarios(usuarios):
    for cpf, dados in usuarios.items():
        print(f"CPF: {cpf} | Nome: {dados['nome']} | Data de Nascimento: {dados['data_nascimento']} | Endereço: {dados['endereco']}")

def main():
    
    saldo = 0
    limite = 500
    extrato = ""
    numero_saques = 0
    LIMITE_SAQUES = 3
    usuarios = {}
    contas = []
    AGENCIA = "0001"

    while True:
        opcao = input(menu_principal())

        if opcao == "d":
            valor = float(input("Informe o valor do depósito: "))
            saldo, extrato = depositar(valor, saldo, extrato)
            print("Depósito realizado com sucesso.")

        elif opcao == "s":
            valor = float(input("Informe o valor do saque: "))
            saldo, numero_saques, extrato = sacar(valor=valor, saldo=saldo, limite=limite, numero_saques=numero_saques, extrato=extrato, limite_saques=LIMITE_SAQUES)

        elif opcao == "e":
            exibir_extrato(saldo, extrato=extrato)

        elif opcao == "u":
            cpf = input("Informe o CPF do usuário: ")
            nome = input("Informe o nome do usuário: ")
            data_nascimento = input("Informe a data de nascimento do usuário (DD/MM/AAAA): ")
            endereco = input("Informe o endereço do usuário: ")
            criar_usuario(usuarios, cpf, nome, data_nascimento, endereco)

        elif opcao == "c":
            cpf = input("Informe o CPF do usuário: ")
            criar_conta_corrente(AGENCIA, usuarios, cpf, contas)
        
        elif opcao == "l":
            listar_usuarios(usuarios)
        
        elif opcao == "lc":
            listar_contas(contas)
        
        elif opcao == "q":
            break

        else:
            print("Operação inválida, por favor selecione novamente a operação desejada.")


main()
