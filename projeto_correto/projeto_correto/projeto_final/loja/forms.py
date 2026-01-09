from django import forms
from .models import Produto, Categoria

class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = [
            'nome',
            'descricao',
            'preco',
            'estoque',
            'categoria',
            'imagem',
        ]

        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Nome do produto'}),
            'descricao': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Descrição do produto'}),
            'preco': forms.NumberInput(attrs={'step': '0.01'}),
            'estoque': forms.NumberInput(),
            'categoria': forms.Select(),
        }

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome']

        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Nome da categoria'})
        }
