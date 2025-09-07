from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
db = SQLAlchemy()
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    preco = db.Column(db.Float, default=0)
    quantidade = db.Column(db.Integer, default=0)
class Anuncio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'), nullable=False)
    preco = db.Column(db.Float, default=0)
    status = db.Column(db.String(50), default='ativo')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    produto = db.relationship('Produto', backref=db.backref('anuncios', lazy=True))
    user = db.relationship('User', backref=db.backref('anuncios', lazy=True))
class Venda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    anuncio_id = db.Column(db.Integer, db.ForeignKey('anuncio.id'), nullable=False)
    comprador = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    anuncio = db.relationship('Anuncio', backref=db.backref('vendas', lazy=True))
    user = db.relationship('User', backref=db.backref('vendas', lazy=True))
