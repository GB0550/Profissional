from .carrinho import Carrinho

def carrinho_context(request):
    return {
        'carrinho': Carrinho(request)
    }
