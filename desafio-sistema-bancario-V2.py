from abc import ABC, abstractmethod
from datetime import datetime


class Transacao(ABC):
    @abstractmethod
    def tipo(self):
        raise NotImplementedError()


class Deposito(Transacao):
    def __init__(self, valor):
        self.valor = valor

    def tipo(self):
        return "Depósito"


class Saque(Transacao):
    def __init__(self, valor):
        self.valor = valor

    def tipo(self):
        return "Saque"


class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, tipo, valor):
        self._transacoes.append({
            "tipo": tipo,
            "valor": valor,
            "data": datetime.now(),
        })

    def __str__(self):
        if not self._transacoes:
            return "Não foram realizadas movimentações."

        lines = []
        for t in self._transacoes:
            lines.append(f"{t['data'].strftime('%d/%m/%Y %H:%M:%S')} - {t['tipo']}: R$ {t['valor']:.2f}")
        return "\n".join(lines)


class Conta:
    def __init__(self, saldo, numero, agencia, cliente, historico=None):
        self._saldo = saldo
        self._numero = numero
        self._agencia = agencia
        self._cliente = cliente
        self._historico = historico or Historico()

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    @classmethod
    def nova_conta(cls, cliente, numero, agencia="0001"):
        return cls(0, numero, agencia, cliente, Historico())

    def sacar(self, valor):
        if valor > self._saldo:
            print("Saldo insuficiente.")
            return False

        self._saldo -= valor
        self._historico.adicionar_transacao("Saque", valor)
        return True

    def depositar(self, valor):
        if valor <= 0:
            print("Valor inválido para depósito.")
            return False

        self._saldo += valor
        self._historico.adicionar_transacao("Depósito", valor)
        return True


class ContaCorrente(Conta):
    def __init__(self, saldo, numero, agencia, cliente, historico, limite_saques=3, limite=500):
        super().__init__(saldo, numero, agencia, cliente, historico)
        self._limite_saques = limite_saques
        self._limite = limite

    @property
    def limite_saques(self):
        return self._limite_saques

    @property
    def limite(self):
        return self._limite

    @classmethod
    def criar_conta(cls, cliente, numero, agencia="0001", limite_saques=3, limite=500):
        return cls(0, numero, agencia, cliente, Historico(), limite_saques, limite)

    def sacar(self, valor):
        if valor > self._limite:
            print("Valor do saque excede o limite por operação.")
            return False

        # conta quantos saques foram feitos hoje
        saques_hoje = sum(
            1
            for t in self.historico.transacoes
            if t["tipo"] == "Saque" and t["data"].date() == datetime.now().date()
        )

        if saques_hoje >= self._limite_saques:
            print("Número máximo de saques diários excedido.")
            return False

        return super().sacar(valor)


class Cliente:
    def __init__(self, endereco):
        self._contas = []
        self._endereco = endereco

    @property
    def contas(self):
        return self._contas

    @property
    def endereco(self):
        return self._endereco

    def adicionar_conta(self, conta):
        self._contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, nome, cpf, data_nascimento, endereco):
        super().__init__(endereco)
        self._nome = nome
        self._cpf = cpf
        self._data_nascimento = data_nascimento

    @property
    def nome(self):
        return self._nome

    @property
    def cpf(self):
        return self._cpf

    @property
    def data_nascimento(self):
        return self._data_nascimento

    def __str__(self):
        return f"{self._nome} (CPF: {self._cpf})"


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

class Banco:
    def __init__(self, agencia="0001"):
        self._usuarios = {}  # cpf -> PessoaFisica
        self._contas = []
        self._agencia = agencia

    def criar_usuario(self, nome, cpf, data_nascimento, endereco):
        if cpf in self._usuarios:
            print("Já existe um usuário com esse CPF!")
            return None
        usuario = PessoaFisica(nome, cpf, data_nascimento, endereco)
        self._usuarios[cpf] = usuario
        print("Usuário criado com sucesso!")
        return usuario

    def criar_conta_para_usuario(self, cpf):
        usuario = self._usuarios.get(cpf)
        if not usuario:
            print("Usuário não encontrado, por favor crie um usuário antes de criar uma conta.")
            return None
        numero_conta = len(self._contas) + 1
        conta = ContaCorrente.criar_conta(usuario, numero_conta, agencia=self._agencia)
        self._contas.append(conta)
        usuario.adicionar_conta(conta)
        print(f"Conta criada com sucesso! Número da conta: {numero_conta}")
        return conta

    def listar_usuarios(self):
        for cpf, usuario in self._usuarios.items():
            print(f"CPF: {cpf} | Nome: {usuario.nome} | Data de Nascimento: {usuario.data_nascimento} | Endereço: {usuario.endereco}")

    def listar_contas(self):
        for conta in self._contas:
            cliente = conta.cliente
            nome = getattr(cliente, 'nome', str(cliente))
            print(f"Agência: {conta.agencia} | Conta: {conta.numero} | Usuário: {nome}")

    def run(self):
        while True:
            opcao = input(menu_principal()).strip()

            if opcao == "d":
                conta = int(input("Informe o número da conta para depósito: "))
                conta_encontrada = next((c for c in self._contas if c.numero == conta), None)
                if not conta_encontrada:
                    print("Conta não encontrada.")
                    continue
                valor = float(input("Informe o valor do depósito: "))
                if conta_encontrada.depositar(valor):
                    print("Depósito realizado com sucesso.")

            elif opcao == "s":
                conta = int(input("Informe o número da conta para saque: "))
                conta_encontrada = next((c for c in self._contas if c.numero == conta), None)
                if not conta_encontrada:
                    print("Conta não encontrada.")
                    continue
                valor = float(input("Informe o valor do saque: "))
                if conta_encontrada.sacar(valor):
                    print("Saque realizado com sucesso.")

            elif opcao == "e":
                conta = int(input("Informe o número da conta para extrato: "))
                conta_encontrada = next((c for c in self._contas if c.numero == conta), None)
                if not conta_encontrada:
                    print("Conta não encontrada.")
                    continue
                print("\n================ EXTRATO ================")
                print(str(conta_encontrada.historico))
                print(f"\nSaldo: R$ {conta_encontrada.saldo:.2f}")
                print("==========================================")

            elif opcao == "u":
                cpf = input("Informe o CPF do usuário: ")
                if cpf in self._usuarios:
                    print("Já existe um usuário com esse CPF!")
                    continue

                nome = input("Informe o nome do usuário: ")
                data_nascimento = input("Informe a data de nascimento do usuário (DD/MM/AAAA): ")
                endereco = input("Informe o endereço do usuário: ")
                self.criar_usuario(nome, cpf, data_nascimento, endereco)

            elif opcao == "c":
                cpf = input("Informe o CPF do usuário: ")
                self.criar_conta_para_usuario(cpf)

            elif opcao == "l":
                self.listar_usuarios()

            elif opcao == "lc":
                self.listar_contas()

            elif opcao == "q":
                break

            else:
                print("Operação inválida, por favor selecione novamente a operação desejada.")


def main():
    banco = Banco()
    banco.run()

if __name__ == "__main__":
    main()
