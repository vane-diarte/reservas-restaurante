from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import secrets

app = Flask (__name__)

app.config['SECRET_KEY'] = secrets.token_hex(16)  

app.static_folder = 'static'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reservas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Reserva(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    mesa = db.Column(db.Integer, unique=False, nullable=False)
    cantidad_personas = db.Column(db.Integer, unique=False, nullable=False)
    """ fecha_reserva = db.Column(db.Date, nullable=False) """
   
    
    def __init__(self, username, mesa, cantidad_personas):
       
        self.username = username
        self.mesa = mesa
        self.cantidad_personas = cantidad_personas



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
    """ fecha_reserva = request.form.get("fecha_reserva") """
    

    if username and cantidad_personas and mesa:
        try:
            cantidad_personas = int(cantidad_personas)
            mesa = int(mesa)
            if mesa > 6:
                flash("Número de mesa no válido, ingrese un numero del 1 al 6", "danger")
                return redirect(url_for("index"))
            
            # Comprobar si la mesa ya está reservada
            mesa_reservada = Reserva.query.filter_by(mesa=mesa).first()
            if mesa_reservada:
                flash("La mesa ya está reservada.", "danger")
                return redirect(url_for("index"))
            
            # Verificar si el username ya está en uso
            reserva_existe = Reserva.query.filter_by(username=username).first()
            if reserva_existe:
                flash("El nombre de usuario ya ha sido utilizado para una reserva, ingrese otro nombre", "danger")
                return redirect(url_for("index"))
            
                        
            nueva_reserva = Reserva (username=username, cantidad_personas=cantidad_personas, mesa=mesa)
            db.session.add(nueva_reserva)
            db.session.commit()
            flash("Reserva agregada con éxito.", "success")
        except ValueError:
            flash("Cantidad de personas y mesa deben ser números enteros.", "danger")
    else:
        flash("Todos los campos son obligatorios.", "danger")

    return redirect(url_for("index"))

    

""" modificar reserva """
@app.route("/modificar/<int:reserva_id>", methods=["POST", "GET"])
def modificar(reserva_id):
    mesa = request.form.get ("mesa")
    username = request.form.get ("username")
    cantidad_personas = request.form.get ("cantidad_personas")
    reserva = db.session.query(Reserva).filter(Reserva.id == reserva_id).first()
    
    
    if request.method == 'POST':
        reserva.username = request.form ["username"]
        reserva.mesa = request.form ["mesa"]
        reserva.cantidad_personas = request.form ["cantidad_personas"]
        
        if username and mesa and cantidad_personas:
            try:
                cantidad_personas = int(cantidad_personas)
                mesa = int(mesa)
                if mesa > 6:
                    flash("Número de mesa no válido, ingrese un numero del 1 al 6.", "danger")
                    return render_template("update.html", reserva=reserva)
                
                # Comprobar si la mesa ya está reservada
                mesa_reservada = Reserva.query.filter(Reserva.mesa == mesa, Reserva.id != reserva_id).first()
                if mesa_reservada:
                    flash("La mesa ya está reservada.", "danger")
                    return render_template("update.html", reserva=reserva)
                
                # Verificar si el username ya está en uso
                reserva_existe = Reserva.query.filter(Reserva.username == username, Reserva.id != reserva_id).first()
                if reserva_existe:
                    flash("El nombre de usuario ya ha sido utilizado para una reserva, ingrese otro nombre", "danger")
                    return render_template("update.html", reserva=reserva)
               
                db.session.commit()
                flash("Reserva modificada con éxito.", "success")
                return redirect(url_for("index"))
            except ValueError:
                flash("Cantidad de personas y mesa deben ser números enteros.", "danger")
                return render_template("update.html", reserva=reserva)
        else:
            flash("Todos los campos son obligatorios.", "danger")
            return render_template("update.html", reserva=reserva)

        
        
        
    return render_template ("update.html", reserva = reserva)


""" eliminar reserva """
@app.route("/eliminar/<int:reserva_id>")
def eliminar(reserva_id):
    reserva = db.session.query(Reserva).filter(Reserva.id == reserva_id).first()
    db.session.delete(reserva)
    db.session.commit()
    return redirect(url_for("index"))


if __name__=='__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)


