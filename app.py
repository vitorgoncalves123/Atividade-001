import os
import sys
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Produto, Anuncio, Venda
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'trocasenha')
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:Senha0123!@localhost/atividade03"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
@app.cli.command('initdb')
def initdb():
    with app.app_context():
        db.create_all()
        print('Tabelas criadas')
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('produtos'))
    return redirect(url_for('login'))
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            flash('Preencha usuário e senha')
            return redirect(url_for('register'))
        existing = User.query.filter_by(username=username).first()
        if existing:
            flash('Usuário já existe')
            return redirect(url_for('register'))
        u = User(username=username, password_hash=generate_password_hash(password))
        db.session.add(u)
        db.session.commit()
        login_user(u)
        return redirect(url_for('produtos'))
    return render_template('register.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password_hash, password):
            flash('Credenciais inválidas')
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('produtos'))
    return render_template('login.html')
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
@app.route('/produtos')
@login_required
def produtos():
    lista = Produto.query.all()
    return render_template('produtos.html', produtos=lista)
@app.route('/produtos/novo', methods=['GET', 'POST'])
@login_required
def produto_novo():
    if request.method == 'POST':
        nome = request.form.get('nome')
        descricao = request.form.get('descricao')
        preco = request.form.get('preco') or 0
        quantidade = request.form.get('quantidade') or 0
        p = Produto(nome=nome, descricao=descricao, preco=float(preco), quantidade=int(quantidade))
        db.session.add(p)
        db.session.commit()
        return redirect(url_for('produtos'))
    return render_template('produto_form.html')
@app.route('/produtos/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def produto_editar(id):
    p = Produto.query.get_or_404(id)
    if request.method == 'POST':
        p.nome = request.form.get('nome')
        p.descricao = request.form.get('descricao')
        p.preco = float(request.form.get('preco') or 0)
        p.quantidade = int(request.form.get('quantidade') or 0)
        db.session.commit()
        return redirect(url_for('produtos'))
    return render_template('produto_form.html', produto=p)
@app.route('/produtos/excluir/<int:id>', methods=['POST'])
@login_required
def produto_excluir(id):
    p = Produto.query.get_or_404(id)
    for a in p.anuncios:
        for v in a.vendas:
            db.session.delete(v)
        db.session.delete(a)    
    db.session.delete(p)
    db.session.commit()
    return redirect(url_for('produtos'))

@app.route('/anuncios')
@login_required
def anuncios():
    lista = Anuncio.query.all()
    return render_template('anuncios.html', anuncios=lista)
@app.route('/anuncios/novo', methods=['GET', 'POST'])
@login_required
def anuncio_novo():
    produtos = Produto.query.all()
    if request.method == 'POST':
        produto_id = int(request.form.get('produto_id'))
        preco = float(request.form.get('preco') or 0)
        a = Anuncio(produto_id=produto_id, preco=preco, status='ativo', user_id=current_user.id)
        db.session.add(a)
        db.session.commit()
        return redirect(url_for('anuncios'))
    return render_template('anuncio_form.html', produtos=produtos)
@app.route('/anuncios/excluir/<int:id>', methods=['POST'])
@login_required
def anuncio_excluir(id):
    a = Anuncio.query.get_or_404(id)
    for v in a.vendas:
        db.session.delete(v)

    db.session.delete(a)
    db.session.commit()
    return redirect(url_for('anuncios'))
@app.route('/vendas')
@login_required
def vendas():
    lista = Venda.query.all()
    return render_template('vendas.html', vendas=lista)
@app.route('/vendas/registrar/<int:anuncio_id>', methods=['GET', 'POST'])
@login_required
def venda_registrar(anuncio_id):
    a = Anuncio.query.get_or_404(anuncio_id)
    if request.method == 'POST':
        comprador = request.form.get('comprador')
        v = Venda(anuncio_id=a.id, comprador=comprador, user_id=current_user.id)
        a.status = 'vendido'
        db.session.add(v)
        db.session.commit()
        return redirect(url_for('vendas'))
    return render_template('venda_form.html', anuncio=a)
if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'initdb':
        with app.app_context():
            db.create_all()
            print('Tabelas criadas')
    else:
        app.run()
