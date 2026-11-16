
# Importa as ferramentas necessárias
from flask import Flask, render_template, request
import sqlite3

# Cria a aplicação Flask
app = Flask(__name__)

# Nome do arquivo do banco de dados
BANCO = "estoque.db"


# Cria o banco e a tabela de produtos
def criar_banco():
    conexao = sqlite3.connect(BANCO)

    conexao.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            codigo TEXT NOT NULL UNIQUE,
            categoria TEXT NOT NULL,
            preco REAL NOT NULL,
            quantidade INTEGER NOT NULL
        )
    """)

    conexao.commit()
    conexao.close()


# Página inicial
@app.route("/")
def inicio():
    return """
    <h1>Controle de Estoque</h1>
    <p>Bem-vindo ao nosso sistema!</p>
    <a href="/produtos">Cadastrar produtos</a>
    """


# Cadastro e consulta de produtos
@app.route("/produtos", methods=["GET", "POST"])
def produtos():

    mensagem = ""
    tipo_mensagem = ""

    # Verifica se o formulário foi enviado
    if request.method == "POST":

        # Recebe os dados digitados no formulário
        nome = request.form.get("nome", "").strip()
        codigo = request.form.get("codigo", "").strip()
        categoria = request.form.get("categoria", "").strip()

        try:
            preco = float(request.form.get("preco", ""))
            quantidade = int(request.form.get("quantidade", ""))

            # Valida os dados recebidos
            if not nome or not codigo or not categoria:
                raise ValueError

            if preco < 0 or quantidade < 0:
                raise ValueError

            # Conecta ao banco de dados
            conexao = sqlite3.connect(BANCO)

            # Salva o produto utilizando parâmetros
            conexao.execute("""
                INSERT INTO produtos
                (nome, codigo, categoria, preco, quantidade)
                VALUES (?, ?, ?, ?, ?)
            """, (nome, codigo, categoria, preco, quantidade))

            conexao.commit()
            conexao.close()

            mensagem = "Produto cadastrado com sucesso!"
            tipo_mensagem = "sucesso"

        except ValueError:
            mensagem = "Verifique os campos e informe valores válidos."
            tipo_mensagem = "erro"

        except sqlite3.IntegrityError:
            mensagem = "Já existe um produto com esse código."
            tipo_mensagem = "erro"

    # Busca os produtos cadastrados
    conexao = sqlite3.connect(BANCO)
    conexao.row_factory = sqlite3.Row

    produtos_cadastrados = conexao.execute(
        "SELECT * FROM produtos ORDER BY id DESC"
    ).fetchall()

    conexao.close()

    # Mostra o formulário e a lista de produtos
    return render_template(
        "produtos.html",
        mensagem=mensagem,
        tipo_mensagem=tipo_mensagem,
        produtos=produtos_cadastrados
    )


# Cria o banco antes de iniciar o servidor
if __name__ == "__main__":
    criar_banco()
    app.run(debug=True)
