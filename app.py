from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from models import db, Usuario, Categoria, Anuncio, Compra, Pergunta, Resposta, Favorito
import os

app = Flask(__name__)

from sqlalchemy import event
from sqlalchemy.engine import Engine

@event.listens_for(Engine, "connect")
def _fk_pragma_on_connect(dbapi_con, con_record):
    try:
        cur = dbapi_con.cursor()
        cur.execute("PRAGMA foreign_keys=ON")
        cur.close()
    except Exception:
        pass

app.config["SECRET_KEY"] = "dev-secret"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///database.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route("/")
def index():
    return render_template("index.html")

def get_int(form, key, default=None):
    try:
        return int(form.get(key, default))
    except Exception:
        return default

def get_float(form, key, default=None):
    try:
        return float(form.get(key, default))
    except Exception:
        return default

@app.route("/usuarios")
def usuarios_list():
    usuarios = Usuario.query.all()
    return render_template("usuarios/listar.html", usuarios=usuarios)

@app.route("/usuarios/novo", methods=["GET", "POST"])
def usuarios_create():
    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        u = Usuario(nome=nome, email=email)
        db.session.add(u); db.session.commit()
        flash("Usuário criado com sucesso!")
        return redirect(url_for("usuarios_list"))
    return render_template("usuarios/form.html", usuario=None)

@app.route("/usuarios/editar/<int:id>", methods=["GET", "POST"])
def usuarios_edit(id):
    u = Usuario.query.get_or_404(id)
    if request.method == "POST":
        u.nome = request.form["nome"]
        u.email = request.form["email"]
        db.session.commit()
        flash("Usuário atualizado com sucesso!")
        return redirect(url_for("usuarios_list"))
    return render_template("usuarios/form.html", usuario=u)

@app.route("/usuarios/excluir/<int:id>", methods=["GET", "POST"])
def usuarios_delete(id):
    u = Usuario.query.get_or_404(id)
    if request.method == "POST":
        db.session.delete(u); db.session.commit()
        flash("Usuário excluído com sucesso!")
        return redirect(url_for("usuarios_list"))
    return render_template("usuarios/confirmar_exclusao.html", usuario=u)

@app.route("/categorias")
def categorias_list():
    app.logger.info("Oi")
    categorias = Categoria.query.all()
    return render_template("categorias/listar.html", categorias=categorias)

@app.route("/categorias/novo", methods=["GET", "POST"])
def categorias_create():
    if request.method == "POST":
        nome = request.form["nome"]
        c = Categoria(nome=nome)
        db.session.add(c); db.session.commit()
        flash("Categoria criada com sucesso!")
        return redirect(url_for("categorias_list"))
    return render_template("categorias/form.html", categoria=None)

@app.route("/categorias/editar/<int:id>", methods=["GET", "POST"])
def categorias_edit(id):
    c = Categoria.query.get_or_404(id)
    if request.method == "POST":
        c.nome = request.form["nome"]
        db.session.commit()
        flash("Categoria atualizada com sucesso!")
        return redirect(url_for("categorias_list"))
    return render_template("categorias/form.html", categoria=c)

@app.route("/categorias/excluir/<int:id>", methods=["GET", "POST"])
def categorias_delete(id):
    c = Categoria.query.get_or_404(id)
    if request.method == "POST":
        db.session.delete(c); db.session.commit()
        flash("Categoria excluída com sucesso!")
        return redirect(url_for("categorias_list"))
    return render_template("categorias/confirmar_exclusao.html", categoria=c)

@app.route("/anuncios")
def anuncios_list():
    anuncios = Anuncio.query.all()
    categorias = Categoria.query.all()
    usuarios = Usuario.query.all()
    return render_template("anuncios/listar.html", anuncios=anuncios, categorias=categorias, usuarios=usuarios)

@app.route("/anuncios/novo", methods=["GET", "POST"])
def anuncios_create():
    if request.method == "POST":
        titulo = request.form["titulo"]
        descricao = request.form.get("descricao")
        preco = get_float(request.form, "preco", 0.0)
        categoria_id = get_int(request.form, "categoria_id")
        usuario_id = get_int(request.form, "usuario_id")
        a = Anuncio(titulo=titulo, descricao=descricao, preco=preco, categoria_id=categoria_id, usuario_id=usuario_id)
        db.session.add(a); db.session.commit()
        flash("Anúncio criado com sucesso!")
        return redirect(url_for("anuncios_list"))
    categorias = Categoria.query.all()
    usuarios = Usuario.query.all()
    return render_template("anuncios/form.html", anuncio=None, categorias=categorias, usuarios=usuarios)

@app.route("/anuncios/editar/<int:id>", methods=["GET", "POST"])
def anuncios_edit(id):
    a = Anuncio.query.get_or_404(id)
    if request.method == "POST":
        a.titulo = request.form["titulo"]
        a.descricao = request.form.get("descricao")
        a.preco = get_float(request.form, "preco", a.preco)
        a.categoria_id = get_int(request.form, "categoria_id", a.categoria_id)
        a.usuario_id = get_int(request.form, "usuario_id", a.usuario_id)
        db.session.commit()
        flash("Anúncio atualizado com sucesso!")
        return redirect(url_for("anuncios_list"))
    categorias = Categoria.query.all()
    usuarios = Usuario.query.all()
    return render_template("anuncios/form.html", anuncio=a, categorias=categorias, usuarios=usuarios)

@app.route("/anuncios/excluir/<int:id>", methods=["GET", "POST"])
def anuncios_delete(id):
    a = Anuncio.query.get_or_404(id)
    if request.method == "POST":
        db.session.delete(a); db.session.commit()
        flash("Anúncio excluído com sucesso!")
        return redirect(url_for("anuncios_list"))
    return render_template("anuncios/confirmar_exclusao.html", anuncio=a)

@app.route("/compras")
def compras_list():
    compras = Compra.query.all()
    return render_template("compras/listar.html", compras=compras)

@app.route("/compras/novo", methods=["GET", "POST"])
def compras_create():
    if request.method == "POST":
        usuario_id = get_int(request.form, "usuario_id")
        anuncio_id = get_int(request.form, "anuncio_id")
        quantidade = get_int(request.form, "quantidade", 1)
        total = get_float(request.form, "total", 0.0)
        c = Compra(usuario_id=usuario_id, anuncio_id=anuncio_id, quantidade=quantidade, total=total)
        db.session.add(c); db.session.commit()
        flash("Compra registrada com sucesso!")
        return redirect(url_for("compras_list"))
    usuarios = Usuario.query.all()
    anuncios = Anuncio.query.all()
    return render_template("compras/form.html", compra=None, usuarios=usuarios, anuncios=anuncios)

@app.route("/compras/editar/<int:id>", methods=["GET", "POST"])
def compras_edit(id):
    c = Compra.query.get_or_404(id)
    if request.method == "POST":
        c.usuario_id = get_int(request.form, "usuario_id", c.usuario_id)
        c.anuncio_id = get_int(request.form, "anuncio_id", c.anuncio_id)
        c.quantidade = get_int(request.form, "quantidade", c.quantidade)
        c.total = get_float(request.form, "total", c.total)
        db.session.commit()
        flash("Compra atualizada com sucesso!")
        return redirect(url_for("compras_list"))
    usuarios = Usuario.query.all()
    anuncios = Anuncio.query.all()
    return render_template("compras/form.html", compra=c, usuarios=usuarios, anuncios=anuncios)

@app.route("/compras/excluir/<int:id>", methods=["GET", "POST"])
def compras_delete(id):
    c = Compra.query.get_or_404(id)
    if request.method == "POST":
        db.session.delete(c); db.session.commit()
        flash("Compra excluída com sucesso!")
        return redirect(url_for("compras_list"))
    return render_template("compras/confirmar_exclusao.html", compra=c)

@app.route("/perguntas")
def perguntas_list():
    perguntas = Pergunta.query.all()
    return render_template("perguntas/listar.html", perguntas=perguntas)

@app.route("/perguntas/novo", methods=["GET", "POST"])
def perguntas_create():
    if request.method == "POST":
        usuario_id = get_int(request.form, "usuario_id")
        anuncio_id = get_int(request.form, "anuncio_id")
        texto = request.form["texto"]
        p = Pergunta(usuario_id=usuario_id, anuncio_id=anuncio_id, texto=texto)
        db.session.add(p); db.session.commit()
        flash("Pergunta criada com sucesso!")
        return redirect(url_for("perguntas_list"))
    usuarios = Usuario.query.all()
    anuncios = Anuncio.query.all()
    return render_template("perguntas/form.html", pergunta=None, usuarios=usuarios, anuncios=anuncios)

@app.route("/perguntas/editar/<int:id>", methods=["GET", "POST"])
def perguntas_edit(id):
    p = Pergunta.query.get_or_404(id)
    if request.method == "POST":
        p.usuario_id = get_int(request.form, "usuario_id", p.usuario_id)
        p.anuncio_id = get_int(request.form, "anuncio_id", p.anuncio_id)
        p.texto = request.form["texto"]
        db.session.commit()
        flash("Pergunta atualizada com sucesso!")
        return redirect(url_for("perguntas_list"))
    usuarios = Usuario.query.all()
    anuncios = Anuncio.query.all()
    return render_template("perguntas/form.html", pergunta=p, usuarios=usuarios, anuncios=anuncios)

@app.route("/perguntas/excluir/<int:id>", methods=["GET", "POST"])
def perguntas_delete(id):
    p = Pergunta.query.get_or_404(id)
    if request.method == "POST":
        db.session.delete(p); db.session.commit()
        flash("Pergunta excluída com sucesso!")
        return redirect(url_for("perguntas_list"))
    return render_template("perguntas/confirmar_exclusao.html", pergunta=p)

@app.route("/respostas")
def respostas_list():
    respostas = Resposta.query.all()
    return render_template("respostas/listar.html", respostas=respostas)

@app.route("/respostas/novo", methods=["GET", "POST"])
def respostas_create():
    if request.method == "POST":
        pergunta_id = get_int(request.form, "pergunta_id")
        usuario_id = get_int(request.form, "usuario_id")
        texto = request.form["texto"]
        r = Resposta(pergunta_id=pergunta_id, usuario_id=usuario_id, texto=texto)
        db.session.add(r); db.session.commit()
        flash("Resposta criada com sucesso!")
        return redirect(url_for("respostas_list"))
    usuarios = Usuario.query.all()
    perguntas = Pergunta.query.all()
    return render_template("respostas/form.html", resposta=None, usuarios=usuarios, perguntas=perguntas)

@app.route("/respostas/editar/<int:id>", methods=["GET", "POST"])
def respostas_edit(id):
    r = Resposta.query.get_or_404(id)
    if request.method == "POST":
        r.pergunta_id = get_int(request.form, "pergunta_id", r.pergunta_id)
        r.usuario_id = get_int(request.form, "usuario_id", r.usuario_id)
        r.texto = request.form["texto"]
        db.session.commit()
        flash("Resposta atualizada com sucesso!")
        return redirect(url_for("respostas_list"))
    usuarios = Usuario.query.all()
    perguntas = Pergunta.query.all()
    return render_template("respostas/form.html", resposta=r, usuarios=usuarios, perguntas=perguntas)

@app.route("/respostas/excluir/<int:id>", methods=["GET", "POST"])
def respostas_delete(id):
    r = Resposta.query.get_or_404(id)
    if request.method == "POST":
        db.session.delete(r); db.session.commit()
        flash("Resposta excluída com sucesso!")
        return redirect(url_for("respostas_list"))
    return render_template("respostas/confirmar_exclusao.html", resposta=r)

@app.route("/favoritos")
def favoritos_list():
    favoritos = Favorito.query.all()
    return render_template("favoritos/listar.html", favoritos=favoritos)

@app.route("/favoritos/novo", methods=["GET", "POST"])
def favoritos_create():
    if request.method == "POST":
        usuario_id = get_int(request.form, "usuario_id")
        anuncio_id = get_int(request.form, "anuncio_id")
        f = Favorito(usuario_id=usuario_id, anuncio_id=anuncio_id)
        db.session.add(f); db.session.commit()
        flash("Favorito adicionado com sucesso!")
        return redirect(url_for("favoritos_list"))
    usuarios = Usuario.query.all()
    anuncios = Anuncio.query.all()
    return render_template("favoritos/form.html", favorito=None, usuarios=usuarios, anuncios=anuncios)

@app.route("/favoritos/editar/<int:id>", methods=["GET", "POST"])
def favoritos_edit(id):
    f = Favorito.query.get_or_404(id)
    if request.method == "POST":
        f.usuario_id = get_int(request.form, "usuario_id", f.usuario_id)
        f.anuncio_id = get_int(request.form, "anuncio_id", f.anuncio_id)
        db.session.commit()
        flash("Favorito atualizado com sucesso!")
        return redirect(url_for("favoritos_list"))
    usuarios = Usuario.query.all()
    anuncios = Anuncio.query.all()
    return render_template("favoritos/form.html", favorito=f, usuarios=usuarios, anuncios=anuncios)

@app.route("/favoritos/excluir/<int:id>", methods=["GET", "POST"])
def favoritos_delete(id):
    f = Favorito.query.get_or_404(id)
    if request.method == "POST":
        db.session.delete(f); db.session.commit()
        flash("Favorito excluído com sucesso!")
        return redirect(url_for("favoritos_list"))
    return render_template("favoritos/confirmar_exclusao.html", favorito=f)

@app.route("/relatorio-compras")
def relatorio_compras():
    compras = Compra.query.all()
    total = sum([c.total for c in compras])
    return render_template("relatorios/compras.html", compras=compras, total=total)

if __name__ == "__main__":
    app.run(debug=True)
