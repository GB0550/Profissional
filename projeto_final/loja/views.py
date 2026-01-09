from decimal import Decimal

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordChangeView
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy

from .carrinho import Carrinho
from .forms import ProdutoForm
from .models import Cliente  # ← ADICIONADO Pedido, ItemPedido
from .models import Categoria, Contato, ItemPedido, Pedido, Produto, Venda


def home(request):
    """Página inicial com produtos em destaque"""
    produtos_destaque = Produto.objects.filter(ativo=True, destaque=True)[:6]
    categorias = Categoria.objects.filter(ativo=True)
    context = {
        "produtos_destaque": produtos_destaque,
        "categorias": categorias,
    }
    return render(request, "loja/home.html", context)


def produtos(request):
    """Lista todos os produtos com filtro por categoria"""
    categoria_id = request.GET.get("categoria")
    busca = request.GET.get("busca")
    produtos = Produto.objects.filter(ativo=True, estoque__gt=0)

    produtos_lista = Produto.objects.filter(ativo=True)

    if categoria_id:
        produtos_lista = produtos_lista.filter(categoria_id=categoria_id)

    if busca:
        produtos_lista = produtos_lista.filter(
            Q(nome__icontains=busca)
            | Q(descricao__icontains=busca)
            | Q(especificacoes__icontains=busca)
        )

    categorias = Categoria.objects.filter(ativo=True)

    context = {
        "produtos": produtos_lista,
        "categorias": categorias,
        "categoria_selecionada": categoria_id,
        "busca": busca,
    }
    return render(request, "loja/produtos.html", context)


def produto_detalhe(request, produto_id):
    """Exibe detalhes de um produto específico"""

    # BUSCA SEMPRE o produto primeiro 
    produto = get_object_or_404(Produto, id=produto_id)

    # SÓ bloqueia para clientes comuns
    if not request.user.is_staff and not (produto.ativo and produto.estoque > 0):
        messages.warning(request, f"Produto '{produto.nome}' indisponível no momento.")
        return redirect("produtos")

    # Produtos relacionados 
    produtos_relacionados = Produto.objects.filter(
        categoria=produto.categoria, ativo=True, estoque__gt=0
    ).exclude(id=produto_id)[:4]

    context = {
        "produto": produto,
        "produtos_relacionados": produtos_relacionados,
    }
    return render(request, "loja/produto_detalhe.html", context)


def sobre(request):
    """Página sobre a empresa"""
    return render(request, "loja/sobre.html")


def contato(request):
    """Página de contato com formulário"""
    if request.method == "POST":
        nome = request.POST.get("nome")
        email = request.POST.get("email")
        telefone = request.POST.get("telefone", "")
        assunto = request.POST.get("assunto")
        mensagem = request.POST.get("mensagem")

        if nome and email and assunto and mensagem:
            Contato.objects.create(
                nome=nome,
                email=email,
                telefone=telefone,
                assunto=assunto,
                mensagem=mensagem,
            )
            messages.success(
                request, "Mensagem enviada com sucesso! Entraremos em contato em breve."
            )
            return redirect("contato")
        else:
            messages.error(request, "Por favor, preencha todos os campos obrigatórios.")

    return render(request, "loja/contato.html")


def cadastro(request):
    """Página de cadastro de novo usuário"""
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        password = request.POST.get("password")
        password_confirm = request.POST.get("password_confirm")
        cpf = request.POST.get("cpf")
        telefone = request.POST.get("telefone")
        endereco = request.POST.get("endereco")
        cidade = request.POST.get("cidade")
        estado = request.POST.get("estado")
        cep = request.POST.get("cep")

        if password != password_confirm:
            messages.error(request, "As senhas não coincidem.")
            return render(request, "loja/cadastro.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Nome de usuário já existe.")
            return render(request, "loja/cadastro.html")

        if User.objects.filter(email=email).exists():
            messages.error(request, "E-mail já cadastrado.")
            return render(request, "loja/cadastro.html")

        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password,
            )

            Cliente.objects.create(
                usuario=user,
                cpf=cpf,
                telefone=telefone,
                endereco=endereco,
                cidade=cidade,
                estado=estado,
                cep=cep,
            )

            messages.success(
                request, "Cadastro realizado com sucesso! Faça login para continuar."
            )
            return redirect("login")
        except Exception as e:
            messages.error(request, f"Erro ao criar cadastro: {str(e)}")

    return render(request, "loja/cadastro.html")


def login_view(request):
    """Página de login"""
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Bem-vindo, {user.first_name}!")
            next_url = request.GET.get("next", "home")
            return redirect(next_url)
        else:
            messages.error(request, "Usuário ou senha inválidos.")

    return render(request, "registration/login.html")


def logout_view(request):
    """Realiza logout do usuário"""
    logout(request)
    messages.success(request, "Logout realizado com sucesso.")
    return redirect("home")


# carrinho


def carrinho(request):
    carrinho = Carrinho(request)
    return render(request, "loja/carrinho.html", {"carrinho": carrinho})


def adicionar_carrinho(request, produto_id):
    """Adiciona 1 unidade do produto ao carrinho"""
    produto = get_object_or_404(Produto, id=produto_id)
    carrinho = Carrinho(request)
    carrinho.adicionar(produto, quantidade=1)
    messages.success(request, f"{produto.nome} adicionado ao carrinho!")
    return redirect("carrinho")


def diminuir_carrinho(request, produto_id):
    """Remove 1 unidade do produto do carrinho"""
    carrinho = Carrinho(request)
    produto = Produto.objects.get(id=produto_id)
    carrinho.diminuir(produto, quantidade=1)  # ← DIMINUIR, não remover!
    messages.success(request, "Quantidade diminuída!")
    return redirect("carrinho")


def remover_carrinho(request, produto_id):
    """Remove completamente o produto do carrinho"""
    carrinho = Carrinho(request)
    produto = Produto.objects.get(id=produto_id)
    carrinho.remover(produto)
    messages.success(request, "Item removido do carrinho!")
    return redirect("carrinho")


def checkout(request):
    carrinho = Carrinho(request)

    if request.method == "POST":

        # TRANSAÇAO: ou tudo funciona, ou nada funciona
        with transaction.atomic():

            # CLIENTE
            cliente, created = Cliente.objects.get_or_create(
                usuario=request.user,
                defaults={
                    "cpf": request.POST.get("cpf", "000.000.000-00"),
                    "telefone": request.POST.get("telefone", ""),
                    "endereco": request.POST.get("endereco", ""),
                    "cidade": request.POST.get("cidade", ""),
                    "estado": request.POST.get("estado", "SP"),
                    "cep": request.POST.get("cep", ""),
                },
            )

            # PEDIDO
            pedido = Pedido.objects.create(
                cliente=cliente, status="confirmado", valor_total=carrinho.total()
            )

            # ITENS E BAIXA DE ESTOQUE
            for item in carrinho:
                produto = get_object_or_404(Produto, id=item["id"])

                # VERIFICA ESTOQUE
                if produto.estoque < item["quantidade"]:
                    messages.error(request, f"Estoque insuficiente para {produto.nome}")
                    return redirect("carrinho")

                # CRIA ITEM DO PEDIDO
                ItemPedido.objects.create(
                    pedido=pedido,
                    produto=produto,
                    quantidade=item["quantidade"],
                    preco_unitario=item["preco"],
                )

                #  ABAIXA O ESTOQUE AQUI
                produto.estoque -= item["quantidade"]
                produto.save()

            # LIMPA O CARRINHO
            request.session["carrinho"] = {}
            request.session.modified = True

            messages.success(request, f"Pedido #{pedido.id} confirmado com sucesso!")

            return redirect("checkout_sucesso", pedido_id=pedido.id)

    return render(request, "loja/checkout.html", {"carrinho": carrinho})


def checkout_sucesso(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)

    return render(request, "loja/checkout_sucesso.html", {"pedido": pedido})


def historico_compras(request):
    if not request.user.is_authenticated:
        return redirect("login")

    cliente = Cliente.objects.filter(usuario=request.user).first()
    pedidos = (
        Pedido.objects.filter(cliente=cliente).order_by("-data_pedido")
        if cliente
        else []
    )

    return render(request, "loja/historico_compras.html", {"pedidos": pedidos})


@login_required
def perfil(request):
    """Página de perfil do usuário"""

    # Se for admin/staff, mostra perfil diferente
    if request.user.is_staff or request.user.is_superuser:
        if request.method == "POST":
            request.user.first_name = request.POST.get("first_name")
            request.user.last_name = request.POST.get("last_name")
            request.user.email = request.POST.get("email")
            request.user.save()
            messages.success(request, "Perfil atualizado!")
            return redirect("perfil")

        return render(
            request,
            "loja/perfil.html",
            {
                "is_admin": True,
            },
        )

    try:
        cliente = request.user.cliente
    except Cliente.DoesNotExist:
        messages.error(request, "Perfil não encontrado.")
        return redirect("home")

    if request.method == "POST":
        request.user.first_name = request.POST.get("first_name")
        request.user.last_name = request.POST.get("last_name")
        request.user.email = request.POST.get("email")
        request.user.save()

        cliente.telefone = request.POST.get("telefone")
        cliente.endereco = request.POST.get("endereco")
        cliente.cidade = request.POST.get("cidade")
        cliente.estado = request.POST.get("estado")
        cliente.cep = request.POST.get("cep")
        cliente.save()

        messages.success(request, "Perfil atualizado com sucesso!")
        return redirect("perfil")

    context = {
        "cliente": cliente,
        "is_admin": False,
    }
    return render(request, "loja/perfil.html", context)


class MinhaPasswordChangeView(PasswordChangeView):
    template_name = "alterar_senha.html"
    success_url = reverse_lazy("sua_url_sucesso")


##
# PAINEL ADMIN - PRODUTOS CRUD
##


@staff_member_required
def painel_admin(request):
    return render(request, "loja/admin/painel.html")


@staff_member_required
def admin_produtos(request):
    produtos = Produto.objects.all()
    return render(request, "loja/admin/produtos/listar.html", {"produtos": produtos})


@staff_member_required
def admin_criar_produto(request):
    if request.method == "POST":
        form = ProdutoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("admin_produtos")
    else:
        form = ProdutoForm()

    return render(request, "loja/admin/produtos/criar.html", {"form": form})


@staff_member_required
def admin_editar_produto(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    categorias = Categoria.objects.all()

    if request.method == "POST":
        produto.nome = request.POST["nome"]
        produto.preco = request.POST["preco"]
        produto.categoria_id = request.POST["categoria"]
        produto.descricao = request.POST.get("descricao")
        produto.especificacoes = request.POST.get("especificacoes")

        if request.FILES.get("imagem"):
            produto.imagem = request.FILES["imagem"]

        produto.save()
        messages.success(request, "Produto atualizado!")
        return redirect("admin_produtos")

    return render(
        request,
        "loja/admin/produtos/editar.html",
        {"produto": produto, "categorias": categorias},
    )


@staff_member_required
def admin_deletar_produto(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    produto.delete()
    messages.success(request, "Produto deletado com sucesso!")
    return redirect("admin_produtos")


##
# PAINEL ADMIN - CATEGORIAS CRUD
##


@staff_member_required
def admin_categorias(request):
    categorias = Categoria.objects.all()
    return render(
        request, "loja/admin/categorias/listar.html", {"categorias": categorias}
    )


@staff_member_required
def admin_criar_categoria(request):
    if request.method == "POST":
        Categoria.objects.create(nome=request.POST["nome"])
        messages.success(request, "Categoria criada!")
        return redirect("admin_categorias")

    return render(request, "loja/admin/categorias/criar.html")


@staff_member_required
def admin_editar_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)

    if request.method == "POST":
        categoria.nome = request.POST["nome"]
        categoria.save()
        messages.success(request, "Categoria atualizada!")
        return redirect("admin_categorias")

    return render(
        request, "loja/admin/categorias/editar.html", {"categoria": categoria}
    )


@staff_member_required
def admin_deletar_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    categoria.delete()
    messages.success(request, "Categoria deletada!")
    return redirect("admin_categorias")


##
# vendas listar
##


@staff_member_required
def admin_vendas(request):
    vendas = ItemPedido.objects.select_related("produto", "pedido").order_by(
        "-pedido__data_pedido"
    )
    return render(request, "loja/admin/vendas/listar.html", {"vendas": vendas})


class MinhaPasswordChangeView(PasswordChangeView):
    template_name = "registration/alterar_senha.html"
    success_url = reverse_lazy("perfil")
