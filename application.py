#from crypt import methods
from distutils.log import error
from http.client import NotConnected
from operator import ge
import os
import re
from socket import errorTab
from unittest import result
from click import password_option

from flask import Blueprint, flash, g,redirect, render_template, Flask, request, session, abort, url_for, current_app, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, apology
import requests

app = Flask(__name__)

# Check for environment variable
#if not os.getenv("DATABASE_URL"):
#   raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
Session(app)

# Set up database
engine = create_engine("postgresql://setruvhdhepzne:14dde31f92e7cfd1bed1083f125402dc352cd503bc851057fccddafca4b5c551@ec2-34-227-135-211.compute-1.amazonaws.com:5432/dd7jm4tkdkdbed")
llave = os.getenv("llave")

db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index():
    if request.method == "GET":
        return render_template("index.html")
    else:
        return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method =='POST':
        if not request.form.get('username'):
            flash("escriba un nombre")
        elif not request.form.get("password"):
            flash("escriba una contraseña")
        
        else:
            usuario = db.execute("SELECT * FROM usuarios WHERE username = :username", {"username": request.form.get('username')}).fetchall()
            
            if len(usuario) != 1 or not check_password_hash(usuario[0]["password"], request.form.get("password")):
               # print(usuario.password)
                flash("Error usuario o contraseña incorrecta") 
               
            else: 
                print(usuario)
                session["user_id"] = usuario[0]["id"] 
                
                return render_template("index.html")
            

    return render_template("login.html")
        

@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "GET":
        return render_template("register.html")

    else:
        username = request.form.get("username")
        password = request.form.get("password")
        
        if not username:
            flash("Ingrese un nombre")
            return render_template("register.html")
        if not password:
            flash("Ingrese una contrasña")
            return render_template("register.html")

        hash = generate_password_hash(password)

        consulta = db.execute("SELECT * FROM usuarios WHERE username = :username",
        {"username": username }).fetchone()

        if consulta :
            flash("Ese nombre ya existe")
            return render_template("register.html")

        nuevo_usuario = db.execute(f"INSERT INTO usuarios (username, password) VALUES(:username, :password) RETURNING id", {"username": username, "password": hash}).fetchone()

    session["user_id"] = nuevo_usuario
    db.commit()
    return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/libros_libros", methods=["GET","POST"])
def busqueda():

    buscar = request.form.get("buscar")
    resultados = []
    
    d =  f"%{buscar}%"
    resultados = db.execute("SELECT * FROM libros WHERE isbn LIKE :buscar or title LIKE :buscar or author LIKE :buscar or year LIKE :buscar", {"buscar": d }).fetchall()

    return render_template("libros_libros.html", resultados=resultados, buscar=buscar)    

    #HASTA AQUI VA BIEN

@app.route("/libro/<isbn>", methods=["GET", "POST"])
def libro(isbn):
    usuarios_id = session.get("user_id")

    if usuarios_id:
        libro = db.execute("SELECT * FROM libros WHERE isbn = :isbn", {"isbn": isbn}).fetchone()

        if libro is None:
            flash("error")
        else:
            if request.method == "POST":
                db.execute(" INSERT INTO critica (comentario, puntaje, usuarios_id, libros_id)  VALUES (:comentario, :puntaje, :usuarios_id, :libros_id); ", 
                {"comentario": request.form.get('comentario'),
                "puntaje": request.form.get('puntaje'),"usuarios_id":usuarios_id, "libros_id": libro.id})

                db.commit()
                return redirect(url_for("libro", isbn=isbn))
            else:
                comentario = db.execute(" SELECT usuarios_id, comentario, puntaje, username FROM critica JOIN usuarios ON usuarios.id=critica.usuarios_id WHERE libros_id=:libros_id ", {"libros_id": libro.id}).fetchall()

                lectura = {}
                if current_app.config.get("llave"):
                    res = request.get("https://www.goodreads.com/libro/critica.json", 
                    parametros = {"key": current_app.config.get("llave"), "isbn": isbn }, timeout=5)

                    if res.status_code != 200:
                        raise Exception("ERROR NO TUVO EXITO")
                    lectura = (res.json())["libros"][0]

                return render_template("libro.html", libro=libro, comentario=comentario, usuarios_id= int(usuarios_id), lectura=lectura)
        
    else:
        abort(403)


@app.route("/api/libro/<isbn>", methods=["GET", "POST"])
def libro_api(isbn):

    libro = db.execute("SELECT libros.id, libros.title, libros.author, libros.year, COUNT(critica.puntaje) AS review_count, AVG(critica.puntaje) AS average_score FROM libros LEFT JOIN critica ON libros.id= critica.libros_id WHERE libros.isbn=:isbn GROUP BY libros.id ",{"isbn": isbn}).fetchone()

    if libro is None:
        return jsonify({"ERROR ":404}), 404
    else:
        if libro.average_score is not None:
            average_score = round(float(libro.average_score), 2)
        else:
            average_score = None

        return jsonify({
            "isbn": isbn,
            "title": libro.title,
            "author": libro.author,
            "year": libro.year,
            "review_count": libro.review_count,
            "average_score": libro.average_score
        })
