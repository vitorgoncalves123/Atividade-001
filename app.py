from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/cadastro")
def cadastro():
    return render_template("cadastro.html")

@app.route("/perfil")
def perfil():
    return render_template("perfil.html")

@app.route("/categorias")
def categorias():
    return render_template("categorias.html")

@app.route("/anuncios")
def anuncios():
    return render_template("anuncios.html")

@app.route("/anuncio/<int:id>")
def anuncio(id):
    return render_template("anuncio.html", id=id)

@app.route("/favoritos")
def favoritos():
    return render_template("favoritos.html")

@app.route("/relatorio-compras")
def relatorio_compras():
    return render_template("relatorio_compras.html")

@app.route("/relatorio-vendas")
def relatorio_vendas():
    return render_template("relatorio_vendas.html")

if __name__ == "__main__":
    app.run(debug=True)
