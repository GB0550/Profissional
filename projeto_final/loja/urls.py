from django.urls import path

from . import views

urlpatterns = [
    # Páginas principais
    path("", views.home, name="home"),
    path("produtos/", views.produtos, name="produtos"),
    path("produto/<int:produto_id>/", views.produto_detalhe, name="produto_detalhe"),
    path("sobre/", views.sobre, name="sobre"),
    path("contato/", views.contato, name="contato"),
    path("cadastro/", views.cadastro, name="cadastro"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("perfil/", views.perfil, name="perfil"),
    # CARRINHO
    path("carrinho/", views.carrinho, name="carrinho"),
    path(
        "carrinho/adicionar/<int:produto_id>/",
        views.adicionar_carrinho,
        name="adicionar_carrinho",
    ),
    path(
        "carrinho/<int:produto_id>/diminuir/",
        views.diminuir_carrinho,
        name="diminuir_carrinho",
    ),
    path(
        "carrinho/remover/<int:produto_id>/",
        views.remover_carrinho,
        name="remover_carrinho",
    ),
    path("minhas-compras/", views.historico_compras, name="historico_compras"),
    #  CHECKOUT
    path("checkout/", views.checkout, name="checkout"),
    path("checkout_sucesso", views.checkout_sucesso, name="checkout_sucesso"),
    path(
        "checkout/sucesso/<int:pedido_id>/",
        views.checkout_sucesso,
        name="checkout_sucesso",
    ),
    path(
        "alterar-senha/",
        views.MinhaPasswordChangeView.as_view(),
        name="password_change",
    ),
    # Painel principal
    path("painel/", views.painel_admin, name="painel_admin"),
    path("painel/vendas/", views.admin_vendas, name="admin_vendas"),
    # PRODUTOS
    path("painel/produtos/", views.admin_produtos, name="admin_produtos"),
    path(
        "painel/produtos/criar/", views.admin_criar_produto, name="admin_criar_produto"
    ),
    path(
        "painel/produtos/editar/<int:produto_id>/",
        views.admin_editar_produto,
        name="admin_editar_produto",
    ),
    path(
        "painel/produtos/deletar/<int:produto_id>/",
        views.admin_deletar_produto,
        name="admin_deletar_produto",
    ),
    # CATEGORIAS
    path("painel/categorias/", views.admin_categorias, name="admin_categorias"),
    path(
        "painel/categorias/criar/",
        views.admin_criar_categoria,
        name="admin_criar_categoria",
    ),
    path(
        "painel/categorias/editar/<int:categoria_id>/",
        views.admin_editar_categoria,
        name="admin_editar_categoria",
    ),
    path(
        "painel/categorias/deletar/<int:categoria_id>/",
        views.admin_deletar_categoria,
        name="admin_deletar_categoria",
    ),
    # Vendas duplicada removida
    # path("painel/vendas/", views.admin_vendas, name="admin_vendas"),  # ← REMOVIDA (duplicada)
]
