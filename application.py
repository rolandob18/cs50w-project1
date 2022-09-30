import os

from flask import flash,redirect, render_template, Flask, request, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, apology

app = Flask(__name__)

# Check for environment variable
#if not os.getenv("DATABASE_URL"):
#   raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine("postgresql://setruvhdhepzne:14dde31f92e7cfd1bed1083f125402dc352cd503bc851057fccddafca4b5c551@ec2-34-227-135-211.compute-1.amazonaws.com:5432/dd7jm4tkdkdbed")
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        if not request.form.get("username"):
            flash("Ingrese un nombre de usuario")
            return render_template("login.html")

        elif not request.form.get("password"):
            flash("Ingrese una contraseña")
            return render_template("login.html")

        consulta = db.execute("SELECT * FROM usuarios = ?", request.form.get("username"))
        
        if len(consulta) != 1 or not check_password_hash(consulta[0]["password"], request.form.get("password")):
            flash("El usuario no existe o la contraseña no es correcta")
            return render_template("login.html")

        session["user_id"] = consulta[0]["id"]
        return redirect("/")

    else:
        return render_template("login.html")


@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "GET":
        return render_template("register.html")

    else:
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            flash("Ingrese un nombre")
            return render_template("register.html")
        if not password:
            flash("Ingrese una contrasña")
            return render_template("register.html")
        if not confirmation:
            flash("confirme su contraseña")
            return render_template("register.html")

        hash = generate_password_hash(password)

        consulta = db.execute("SELECT * FROM usuarios WHERE username = :username", {
            "username": username
        }).fetchone()

        if consulta :
            flash("Ese nombre ya existe")
            return render_template("register.html")

        nuevo_usuario = db.execute(f"INSERT INTO usuarios (username, password) VALUES(:username, :password) RETURNING id", {"username": username, "password": password}).fetchone()

    print(nuevo_usuario)
    session["user_id"] = nuevo_usuario
    db.commit()
    return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")