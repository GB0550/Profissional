from django.shortcuts import get_object_or_404
from .models import Produto

def get_produto(produto_id):
    return get_object_or_404(Produto, id=produto_id)

def calcular_subtotal(preco, quantidade):
    return preco * quantidade

def formatar_preco(valor):
    return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')


