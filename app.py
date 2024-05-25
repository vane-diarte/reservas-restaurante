from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import secrets
from datetime import datetime

app = Flask (__name__)

app.config['SECRET_KEY'] = secrets.token_hex(16)  

app.static_folder = 'static'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reservas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Reserva(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mesa = db.Column(db.Integer, unique=False, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    cantidad_personas = db.Column(db.Integer, unique=False, nullable=False)
    fecha_reserva = db.Column(db.Date, nullable=False)
   
    
    def __init__(self, mesa, username, cantidad_personas, fecha_reserva):
       
        self.mesa = mesa
        self.username = username
        self.cantidad_personas = cantidad_personas
        self.fecha_reserva = fecha_reserva



""" rutas """
@app.route('/')
def index():
    reservas = db.session.query(Reserva).all()
    return render_template ('index.html', reservas = reservas)

""" agregar reserva """
@app.route("/add", methods=["POST"])
def add():
    mesa = request.form.get ("mesa")
    username = request.form.get ("username")
    cantidad_personas = request.form.get ("cantidad_personas")
    fecha_reserva = request.form.get("fecha_reserva")
    

    if mesa and username and cantidad_personas and fecha_reserva:
        try:
            cantidad_personas = int(cantidad_personas)
            mesa = int(mesa)
            fecha_reserva = datetime.strptime(fecha_reserva, '%Y-%m-%d').date()  # Convertir a fecha
            
            if mesa > 6:
                flash("Número de mesa no válido, ingrese un numero del 1 al 6", "danger")
                return redirect(url_for("index"))
            
            # Comprobar si la mesa ya está reservada para esa fecha
            mesa_reservada = Reserva.query.filter_by(mesa=mesa, fecha_reserva=fecha_reserva).first()
            if mesa_reservada:
                flash("La mesa ya está reservada para esta fecha.", "danger")
                return redirect(url_for("index"))
            
            # Verificar si el username ya está en uso
            reserva_existe = Reserva.query.filter_by(username=username).first()
            if reserva_existe:
                flash("El nombre de usuario ya ha sido utilizado para una reserva, ingrese otro nombre", "danger")
                return redirect(url_for("index"))
            
            nueva_reserva = Reserva (mesa, username, cantidad_personas, fecha_reserva)
            db.session.add(nueva_reserva)
            db.session.commit()
            flash("Reserva agregada con éxito.", "success")
            return redirect(url_for("index"))
               
        except ValueError:
            flash("Cantidad de personas y mesa deben ser números enteros.", "danger")
            return redirect(url_for("index"))
            
    else:
        flash("Todos los campos son obligatorios.", "danger")
        return redirect(url_for("index"))

    

""" modificar reserva """
@app.route("/modificar/<int:reserva_id>", methods=["POST", "GET"])
def modificar(reserva_id):
    
    reserva = Reserva.query.get(reserva_id)
    
    
    if request.method == 'POST':
        mesa = request.form.get ("mesa")
        username = request.form.get ("username")
        cantidad_personas = request.form.get ("cantidad_personas")
        fecha_reserva = request.form.get("fecha_reserva")
        
        if username and mesa and cantidad_personas and fecha_reserva:
            try:
                cantidad_personas = int(cantidad_personas)
                mesa = int(mesa)
                fecha_reserva = datetime.strptime(fecha_reserva, '%Y-%m-%d').date()  # Convertir a fecha
                
                if mesa > 6:
                    flash("Número de mesa no válido, ingrese un numero del 1 al 6.", "danger")
                    return render_template("update.html", reserva=reserva)
                
                # Comprobar si la mesa ya está reservada para esa fecha
                mesa_reservada = Reserva.query.filter(Reserva.mesa == mesa, Reserva.fecha_reserva == fecha_reserva, Reserva.id != reserva_id).first()
                if mesa_reservada:
                    flash("La mesa ya está reservada para esta fecha.", "danger")
                    return render_template("update.html", reserva=reserva)
                
                # Verificar si el username ya está en uso
                reserva_existe = Reserva.query.filter(Reserva.username == username, Reserva.id != reserva_id).first()
                if reserva_existe:
                    flash("El nombre de usuario ya ha sido utilizado para una reserva, ingrese otro nombre", "danger")
                    return render_template("update.html", reserva=reserva)
                
                # Actualizar los atributos de la reserva con los nuevos valores
                reserva.mesa = mesa
                reserva.username = username
                reserva.cantidad_personas = cantidad_personas
                reserva.fecha_reserva = fecha_reserva
                
                db.session.commit()
                flash("Reserva modificada con éxito.", "success")
                return redirect(url_for("index"))
            
            except ValueError:
                flash("Cantidad de personas y mesa deben ser números enteros.", "danger")
                return render_template("update.html", reserva=reserva)
        else:
            flash("Todos los campos son obligatorios.", "danger")
            return render_template("update.html", reserva=reserva)

        
        
    reserva = Reserva.query.get(reserva_id)        
    return render_template ("update.html", reserva = reserva)


""" eliminar reserva """
@app.route("/eliminar/<int:reserva_id>")
def eliminar(reserva_id):
    reserva = db.session.query(Reserva).filter(Reserva.id == reserva_id).first()
    db.session.delete(reserva)
    db.session.commit()
    return redirect(url_for("index"))





