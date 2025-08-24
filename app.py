from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Usuario, Compra, Venda, Pergunta, Resposta
import os

app = Flask(__name__)
from functools import wraps

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

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")
        if not email or not senha:
            flash("Informe email e senha.", "warning")
            return render_template("login.html")
        user = Usuario.query.filter_by(email=email).first()
        if user and user.verificar_senha(senha):
            session["usuario_id"] = user.id
            session["usuario_nome"] = user.nome
            flash("Login realizado com sucesso!", "success")
            next_url = request.args.get("next") or url_for("index")
            return redirect(next_url)
        else:
            flash("Email ou senha inválidos.", "danger")
    return render_template("login.html")

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = request.form.get("senha")
        if not nome or not email or not senha:
            flash("Preencha todos os campos.", "warning")
            return render_template("cadastro.html")
        existente = Usuario.query.filter_by(email=email).first()
        if existente:
            flash("E-mail já cadastrado. Faça login.", "info")
            return redirect(url_for("login"))
        novo = Usuario(nome=nome, email=email)
        novo.set_senha(senha)
        db.session.add(novo)
        db.session.commit()
        flash("Cadastro realizado! Agora faça login.", "success")
        return redirect(url_for("login"))
    return render_template("cadastro.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Você saiu da sua conta.", "info")
    return redirect(url_for("index"))

@app.route("/perfil")
def perfil():
    uid = session.get("usuario_id")
    if not uid:
        flash("Faça login para acessar o perfil.", "warning")
        return redirect(url_for("login"))
    usuario = Usuario.query.get(uid)
    return render_template("perfil.html", usuario=usuario)

PUBLIC_ENDPOINTS = {"index", "login", "cadastro", "static"}

@app.before_request
def require_login():
    from flask import request
    if request.endpoint is None:
        return
    if any([request.endpoint == e or request.endpoint.startswith(e + ".") for e in PUBLIC_ENDPOINTS]):
        return
    if not session.get("usuario_id"):
        return redirect(url_for("login", next=request.path))

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

@app.route("/compras")
def compras_list():
    compras = Compra.query.all()
    return render_template("compras/listar.html", compras=compras)

@app.route("/compras/novo", methods=["GET", "POST"])
def compras_create():
    if request.method == "POST":
        usuario_id = get_int(request.form, "usuario_id")
        quantidade = get_int(request.form, "quantidade", 1)
        c = Compra(usuario_id=usuario_id, quantidade=quantidade)
        db.session.add(c); db.session.commit()
        flash("Compra registrada com sucesso!")
        return redirect(url_for("compras_list"))
    usuarios = Usuario.query.all()
    return render_template("compras/form.html", compra=None, usuarios=usuarios)

@app.route("/compras/editar/<int:id>", methods=["GET", "POST"])
def compras_edit(id):
    c = Compra.query.get_or_404(id)
    if request.method == "POST":
        c.usuario_id = get_int(request.form, "usuario_id", c.usuario_id)
        c.quantidade = get_int(request.form, "quantidade", c.quantidade)
        db.session.commit()
        flash("Compra atualizada com sucesso!")
        return redirect(url_for("compras_list"))
    usuarios = Usuario.query.all()
    return render_template("compras/form.html", compra=c, usuarios=usuarios)

@app.route("/compras/excluir/<int:id>", methods=["GET", "POST"])
def compras_delete(id):
    c = Compra.query.get_or_404(id)
    if request.method == "POST":
        db.session.delete(c); db.session.commit()
        flash("Compra excluída com sucesso!")
        return redirect(url_for("compras_list"))
    return render_template("compras/confirmar_exclusao.html", compra=c)

@app.route("/vendas")
def vendas_list():
    vendas = Venda.query.all()
    return render_template("vendas/listar.html", vendas=vendas)

@app.route("/vendas/novo", methods=["GET", "POST"])
def vendas_create():
    if request.method == "POST":
        usuario_id = get_int(request.form, "usuario_id")
        quantidade = get_int(request.form, "quantidade", 1)
        c = Venda(usuario_id=usuario_id, quantidade=quantidade)
        db.session.add(c); db.session.commit()
        flash("Venda registrada com sucesso!")
        return redirect(url_for("vendas_list"))
    usuarios = Usuario.query.all()
    return render_template("vendas/form.html", venda=None, usuarios=usuarios)

@app.route("/vendas/editar/<int:id>", methods=["GET", "POST"])
def vendas_edit(id):
    c = Venda.query.get_or_404(id)
    if request.method == "POST":
        c.usuario_id = get_int(request.form, "usuario_id", c.usuario_id)
        c.quantidade = get_int(request.form, "quantidade", c.quantidade)
        db.session.commit()
        flash("Venda atualizada com sucesso!")
        return redirect(url_for("vendas_list"))
    usuarios = Usuario.query.all()
    return render_template("vendas/form.html", venda=c, usuarios=usuarios)

@app.route("/vendas/excluir/<int:id>", methods=["GET", "POST"])
def vendas_delete(id):
    c = Venda.query.get_or_404(id)
    if request.method == "POST":
        db.session.delete(c); db.session.commit()
        flash("Venda excluída com sucesso!")
        return redirect(url_for("vendas_list"))
    return render_template("vendas/confirmar_exclusao.html", venda=c)


@app.route("/perguntas")
def perguntas_list():
    perguntas = Pergunta.query.all()
    return render_template("perguntas/listar.html", perguntas=perguntas)

@app.route("/perguntas/novo", methods=["GET", "POST"])
def perguntas_create():
    if request.method == "POST":
        usuario_id = get_int(request.form, "usuario_id")
        texto = request.form["texto"]
        p = Pergunta(usuario_id=usuario_id, texto=texto)
        db.session.add(p); db.session.commit()
        flash("Pergunta criada com sucesso!")
        return redirect(url_for("perguntas_list"))
    usuarios = Usuario.query.all()
    return render_template("perguntas/form.html", pergunta=None, usuarios=usuarios)

@app.route("/perguntas/editar/<int:id>", methods=["GET", "POST"])
def perguntas_edit(id):
    p = Pergunta.query.get_or_404(id)
    if request.method == "POST":
        p.usuario_id = get_int(request.form, "usuario_id", p.usuario_id)
        p.texto = request.form["texto"]
        db.session.commit()
        flash("Pergunta atualizada com sucesso!")
        return redirect(url_for("perguntas_list"))
    usuarios = Usuario.query.all()
    return render_template("perguntas/form.html", pergunta=p, usuarios=usuarios)

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

if __name__ == "__main__":
    app.run(debug=True)
