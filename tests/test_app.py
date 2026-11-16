
import app as app_module


def configurar_banco_de_teste(monkeypatch, tmp_path):
    # Cria um banco separado para os testes
    banco_teste = tmp_path / "teste.db"

    # Faz a aplicação utilizar esse banco temporário
    monkeypatch.setattr(app_module, "BANCO", str(banco_teste))

    # Cria a tabela de produtos
    app_module.criar_banco()

    # Permite realizar solicitações como se fosse um navegador
    app_module.app.config["TESTING"] = True

    return app_module.app.test_client()


def test_cadastrar_produto(monkeypatch, tmp_path):
    cliente = configurar_banco_de_teste(monkeypatch, tmp_path)

    resposta = cliente.post("/produtos", data={
        "nome": "Camiseta Básica Azul",
        "codigo": "CAM001",
        "categoria": "Roupas",
        "preco": "49.90",
        "quantidade": "15"
    })

    assert resposta.status_code == 200
    assert b"Produto cadastrado com sucesso!" in resposta.data
    assert b"Camiseta Basica Azul" in resposta.data or b"Camiseta B" in resposta.data


def test_impedir_codigo_duplicado(monkeypatch, tmp_path):
    cliente = configurar_banco_de_teste(monkeypatch, tmp_path)

    dados = {
        "nome": "Camiseta Azul",
        "codigo": "CAM001",
        "categoria": "Roupas",
        "preco": "49.90",
        "quantidade": "15"
    }

    # Primeiro cadastro
    cliente.post("/produtos", data=dados)

    # Segundo cadastro com o mesmo código
    resposta = cliente.post("/produtos", data=dados)

    assert b"Ja existe um produto" in resposta.data or b"J\xc3\xa1 existe um produto" in resposta.data


def test_rejeitar_valores_negativos(monkeypatch, tmp_path):
    cliente = configurar_banco_de_teste(monkeypatch, tmp_path)

    resposta = cliente.post("/produtos", data={
        "nome": "Camiseta Azul",
        "codigo": "CAM002",
        "categoria": "Roupas",
        "preco": "-10",
        "quantidade": "5"
    })

    assert b"Verifique os campos" in resposta.data
