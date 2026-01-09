from django.contrib import admin
from .models import Categoria, Produto, Cliente, Pedido, ItemPedido, Contato
from .models import Contato



@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'ativo']
    list_filter = ['ativo']
    search_fields = ['nome', 'descricao']


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'categoria', 'preco', 'estoque', 'destaque', 'ativo', 'data_cadastro']
    list_filter = ['categoria', 'destaque', 'ativo', 'data_cadastro']
    search_fields = ['nome', 'descricao', 'especificacoes']
    list_editable = ['preco', 'estoque', 'destaque', 'ativo']
    date_hierarchy = 'data_cadastro'


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'cpf', 'telefone', 'cidade', 'estado', 'data_cadastro']
    list_filter = ['estado', 'data_cadastro']
    search_fields = ['usuario__first_name', 'usuario__last_name', 'cpf', 'telefone']
    date_hierarchy = 'data_cadastro'


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    readonly_fields = ['subtotal_admin']
    fields = ['produto', 'quantidade', 'preco_unitario', 'subtotal_admin']

    def subtotal_admin(self, obj):
        return obj.subtotal

    subtotal_admin.short_description = 'Subtotal'


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ['id', 'cliente', 'data_pedido', 'status', 'valor_total']
    list_filter = ['status', 'data_pedido']
    search_fields = ['cliente__usuario__first_name', 'cliente__usuario__last_name', 'cliente__cpf']
    date_hierarchy = 'data_pedido'
    inlines = [ItemPedidoInline]


@admin.register(Contato)
class ContatoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'assunto', 'data_envio', 'respondido')
    list_filter = ('respondido', 'data_envio')
    search_fields = ('nome', 'email', 'assunto', 'mensagem')
    date_hierarchy = 'data_envio'
    list_editable = ('respondido',)



# Personalização do Admin
admin.site.site_header = 'JHG CELL - Administração'
admin.site.site_title = 'JHG CELL Admin'
admin.site.index_title = 'Painel de Controle'
