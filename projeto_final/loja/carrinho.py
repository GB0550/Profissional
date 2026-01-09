from decimal import Decimal

class Carrinho:
    def __init__(self, request):
        self.session = request.session
        self.carrinho = self.session.get('carrinho', {})

    def adicionar(self, produto, quantidade=1):
        """
        Adiciona produto respeitando o estoque disponível
        """
        produto_id = str(produto.id)

        quantidade_atual = self.carrinho.get(produto_id, {}).get('quantidade', 0)
        nova_quantidade = quantidade_atual + quantidade

        # NAO permite passar do estoque
        if nova_quantidade > produto.estoque:
            nova_quantidade = produto.estoque

        if produto_id not in self.carrinho:
            self.carrinho[produto_id] = {
                'nome': produto.nome,
                'preco': float(produto.preco),
                'quantidade': nova_quantidade,
                'imagem': getattr(produto.imagem, 'url', '')
            }
        else:
            self.carrinho[produto_id]['quantidade'] = nova_quantidade

        self.salvar()

    def diminuir(self, produto, quantidade=1):
        """
        Diminui a quantidade do produto no carrinho
        """
        produto_id = str(produto.id)

        if produto_id in self.carrinho:
            self.carrinho[produto_id]['quantidade'] -= quantidade

            if self.carrinho[produto_id]['quantidade'] <= 0:
                del self.carrinho[produto_id]

            self.salvar()

    def remover(self, produto):
        """
        Remove o produto completamente do carrinho
        """
        produto_id = str(produto.id)

        if produto_id in self.carrinho:
            del self.carrinho[produto_id]
            self.salvar()

    def salvar(self):
        self.session['carrinho'] = self.carrinho
        self.session.modified = True

    def limpar(self):
        """
        Limpa o carrinho (usado no checkout)
        """
        self.session['carrinho'] = {}
        self.session.modified = True

    def __len__(self):
        return sum(item['quantidade'] for item in self.carrinho.values())

    def __iter__(self):
        """
        Itera de forma compatível com o checkout
        """
        for produto_id, item in self.carrinho.items():
            yield {
                'id': int(produto_id),
                'nome': item['nome'],
                'preco': Decimal(item['preco']),
                'quantidade': item['quantidade'],
                'subtotal': Decimal(item['preco']) * item['quantidade'],
                'imagem': item['imagem'],
            }

    def total(self):
        return sum(
            Decimal(item['preco']) * item['quantidade']
            for item in self.carrinho.values()
        )
