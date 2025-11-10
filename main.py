# ======================================================
# Projeto: Demo POO - Checkout Extensível
# Autor: Thiago Carvalho Rodrigues
# Linguagem: Python
# Paradigma:Orientado a Objetos
# Descrição:
# Simula um sistema de checkout de e-commerce simples.
# O objetivo é demonstrar como a POO usando Abstração,
# Herança e Polimorfismo permite adicionar e trocar
# métodos de pagamento Pix, Cartão, Boleto de forma
# flexível, sem precisar alterar o núcleo do sistema.
# ======================================================

from __future__ import annotations
from abc import ABC, abstractmethod
from time import sleep

# ===== utilidade visual mínima =====
def _cor(txt: str, code="32") -> str:   # 32 verde, 31 vermelho, 33 amarelo, 36 ciano
    return f"\033[{code}m{txt}\033[0m"

def _progresso(msg="Processando"):
    print(_cor(msg, "36"), end="", flush=True)
    for _ in range(6):
        print(".", end="", flush=True); sleep(0.2)
    print()

# ===== núcleo de domínio: produtos/carrinho =====
class Produto:
    # dica: “valores nascem válidos”
    def __init__(self, nome: str, preco: float):
        if preco < 0: raise ValueError("Preço não pode ser negativo.")
        self._nome = nome
        self._preco = preco

    @property
    def nome(self) -> str:   # acesso controlado
        return self._nome

    @property
    def preco(self) -> float:
        return self._preco

class Item:
    def __init__(self, produto: Produto, quantidade: int):
        if quantidade <= 0: raise ValueError("Quantidade deve ser > 0.")
        self.produto = produto
        self.quantidade = quantidade

    def subtotal(self) -> float:
        return self.produto.preco * self.quantidade

class Carrinho:
    # dica: “entrada única”
    def __init__(self):
        self._itens: list[Item] = []

    def adicionar_item(self, produto: Produto, quantidade: int) -> None:
        self._itens.append(Item(produto, quantidade))

    def total(self) -> float:
        return sum(i.subtotal() for i in self._itens)

    def esta_vazio(self) -> bool:
        return not self._itens

    def mostrar(self) -> None:
        print("\n=== Seu carrinho ===")
        for i in self._itens:
            print(f" - {i.quantidade}x {i.produto.nome}  @ R$ {i.produto.preco:.2f}  =  R$ {i.subtotal():.2f}")
        print(f"Total: {_cor(f'R$ {self.total():.2f}', '33')}")

# ===== ABSTRAÇÃO: contrato de pagamento =====
class Pagamento(ABC):
    @abstractmethod
    def nome(self) -> str: ...
    @abstractmethod
    def pagar(self, valor: float) -> bool: ...

# ===== HERANÇA + POLIMORFISMO: estratégias de pagamento =====
class Pix(Pagamento):
    # nota: estado sensível protegido por regra
    def __init__(self, saldo: float):
        self._saldo = max(0.0, saldo)   # ENC: nunca negativo

    def nome(self) -> str:
        return "PIX"

    def pagar(self, valor: float) -> bool:  # POLI: comportamento 1
        _progresso("Validando chave PIX")
        if valor <= self._saldo:
            self._saldo -= valor
            print(_cor("Pagamento PIX aprovado!", "32")); return True
        print(_cor("Saldo PIX insuficiente.", "31")); return False

class CartaoCredito(Pagamento):
    def __init__(self, limite: float):
        self._limite = max(0.0, limite) # ENC: mantém invariante

    def nome(self) -> str:
        return "Cartão de Crédito"

    def pagar(self, valor: float) -> bool:  # POLI: comportamento 2
        _progresso("Autorizando operadora")
        if valor <= self._limite:
            self._limite -= valor
            print(_cor("Transação aprovada no crédito!", "32")); return True
        print(_cor("Limite insuficiente.", "31")); return False

class Boleto(Pagamento):
    def nome(self) -> str:
        return "Boleto"

    def pagar(self, valor: float) -> bool:  # POLI: comportamento 3
        _progresso("Gerando boleto")
        linha = "34191.79001 01043.510047 91020.150008 8 123400000"  # exemplo
        print(_cor("Boleto gerado (pagável em 2 dias).", "33"))
        print("Linha digitável:", linha); return True

# ===== ponto de integração: usa apenas o contrato =====
def processar_checkout(carrinho: Carrinho, metodo: Pagamento) -> None:
    print(f"\n=== Finalizando com {_cor(metodo.nome(), '36')} ===")
    total = carrinho.total()
    print(f"Total a pagar: {_cor(f'R$ {total:.2f}', '33')}")
    aprovado = metodo.pagar(total)     # chamada única (poli em ação)
    if aprovado:
        print(_cor("✅ Recibo", "32")); print("-------------------------------")
        carrinho.mostrar(); print(f"Método: {metodo.nome()}"); print(_cor("Status: PAGO", "32"))
    else:
        print(_cor("❌ Pagamento recusado", "31"))

# ===== interface de linha de comando =====
def main():
    # catálogo curto p/ demo
    catalogo = [Produto("Café 250g", 16.90), Produto("Leite 1L", 5.79), Produto("Biscoito", 4.50)]
    carrinho = Carrinho()

    while True:
        print("\n" + "-"*44)
        print(_cor("==== LOJA POO ====", "36"))
        print("1) Adicionar Café (R$ 16,90)")
        print("2) Adicionar Leite (R$ 5,79)")
        print("3) Adicionar Biscoito (R$ 4,50)")
        print("4) Ver carrinho")
        print("5) Finalizar compra")
        print("0) Sair")
        opc = input("> ").strip()

        if   opc == "1": carrinho.adicionar_item(catalogo[0], 1); print(_cor("+ Café adicionado", "32"))
        elif opc == "2": carrinho.adicionar_item(catalogo[1], 1); print(_cor("+ Leite adicionado", "32"))
        elif opc == "3": carrinho.adicionar_item(catalogo[2], 1); print(_cor("+ Biscoito adicionado", "32"))
        elif opc == "4": carrinho.mostrar() if not carrinho.esta_vazio() else print(_cor("Carrinho vazio.", "31"))
        elif opc == "5":
            if carrinho.esta_vazio():
                print(_cor("Adicione itens antes de pagar.", "31")); continue
            print("\nEscolha o método de pagamento:")
            print("1) PIX (saldo R$ 30,00)")
            print("2) Cartão (limite R$ 1000,00)")
            print("3) Boleto")
            m = input("> ").strip()
            metodo = Pix(30.00) if m == "1" else CartaoCredito(1000.00) if m == "2" else Boleto() if m == "3" else None
            if not metodo: print(_cor("Opção inválida.", "31")); continue
            processar_checkout(carrinho, metodo)
        elif opc == "0": print("Até logo!"); break
        else: print(_cor("Opção inválida.", "31"))

if __name__ == "__main__":
    main()
