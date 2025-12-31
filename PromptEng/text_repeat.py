#Vamos solicitar uma string e um número inteiro como entrada. Depois teremos que retornar a string repetida o número de vezes especificado pelo inteiro.
texto = input("Digite uma string: ")
numero = int(input("Digite um número inteiro: "))
repeticao = (texto + " ") * numero
print("A string repetida é:", repeticao)