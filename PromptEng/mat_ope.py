#Solicitar como entrada dois números e depois vamos realizar uma operação definida pelo usuário
numero1 = float(input("Digite o primeiro número: "))
numero2 = float(input("Digite o segundo número: "))
operacao = input("Digite a operação desejada (+, -, *, /): ")
if operacao == '+':
    resultado = numero1 + numero2
elif operacao == '-':   
    resultado = numero1 - numero2
elif operacao == '*':
    resultado = numero1 * numero2
elif operacao == '/':
    if numero2 != 0:
        resultado = numero1 / numero2
    else:
        resultado = "Erro: Divisão por zero não é permitida."
else:
    resultado = "Operação inválida."
print("O resultado da operação é:", resultado)