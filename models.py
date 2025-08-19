from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = "usuarios"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    # Relationships
    anuncios = db.relationship("Anuncio", backref="dono", lazy=True)
    compras = db.relationship("Compra", backref="cliente", lazy=True)
    perguntas = db.relationship("Pergunta", backref="autor", lazy=True)
    respostas = db.relationship("Resposta", backref="autor_resposta", lazy=True)
    favoritos = db.relationship("Favorito", backref="usuario", lazy=True)

    def __repr__(self):
        return f"<Usuario {self.id} - {self.nome}>"

class Categoria(db.Model):
    __tablename__ = "categorias"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), unique=True, nullable=False)
    anuncios = db.relationship("Anuncio", backref="categoria", lazy=True)

    def __repr__(self):
        return f"<Categoria {self.id} - {self.nome}>"

class Anuncio(db.Model):
    __tablename__ = "anuncios"
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(160), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    preco = db.Column(db.Float, nullable=False, default=0.0)
    categoria_id = db.Column(db.Integer, db.ForeignKey("categorias.id"), nullable=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)
    favoritos = db.relationship("Favorito", backref="anuncio", lazy=True)
    compras = db.relationship("Compra", backref="anuncio", lazy=True)
    perguntas = db.relationship("Pergunta", backref="anuncio", lazy=True)

    def __repr__(self):
        return f"<Anuncio {self.id} - {self.titulo}>"

class Compra(db.Model):
    __tablename__ = "compras"
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    anuncio_id = db.Column(db.Integer, db.ForeignKey("anuncios.id"), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False, default=1)
    total = db.Column(db.Float, nullable=False, default=0.0)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Compra {self.id} - usuario={self.usuario_id} anuncio={self.anuncio_id}>"

class Pergunta(db.Model):
    __tablename__ = "perguntas"
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    anuncio_id = db.Column(db.Integer, db.ForeignKey("anuncios.id"), nullable=False)
    texto = db.Column(db.Text, nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    respostas = db.relationship("Resposta", backref="pergunta", lazy=True)

    def __repr__(self):
        return f"<Pergunta {self.id} - anuncio={self.anuncio_id}>"

class Resposta(db.Model):
    __tablename__ = "respostas"
    id = db.Column(db.Integer, primary_key=True)
    pergunta_id = db.Column(db.Integer, db.ForeignKey("perguntas.id"), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    texto = db.Column(db.Text, nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Resposta {self.id} - pergunta={self.pergunta_id}>"

class Favorito(db.Model):
    __tablename__ = "favoritos"
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    anuncio_id = db.Column(db.Integer, db.ForeignKey("anuncios.id"), nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('usuario_id', 'anuncio_id', name='uq_usuario_anuncio_fav'),)

    def __repr__(self):
        return f"<Favorito {self.id} - usuario={self.usuario_id} anuncio={self.anuncio_id}>"
