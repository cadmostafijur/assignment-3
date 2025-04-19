from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import datetime, date
import pymysql

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# --- Database Connection ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@127.0.0.1/car_workshop'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Models ---
class Mechanic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    car_license = db.Column(db.String(20), nullable=False)
    car_engine = db.Column(db.String(20), nullable=False)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    mechanic_id = db.Column(db.Integer, db.ForeignKey('mechanic.id'), nullable=False)
    appointment_date = db.Column(db.Date, nullable=False)

    client = db.relationship('Client', backref='appointments')
    mechanic = db.relationship('Mechanic', backref='appointments')

# --- Setup (initial dummy mechanics) ---
def setup():
    db.create_all()
    if not Mechanic.query.first():
        mechanics = ['Ali', 'Ahmed', 'Sara', 'John', 'Fatima']
        for name in mechanics:
            db.session.add(Mechanic(name=name))
        db.session.commit()

# --- Routes ---
@app.route('/')
def index():
    mechanics = Mechanic.query.all()
    return render_template('index.html', mechanics=mechanics)

@app.route('/slots')
def get_slots():
    selected_date = request.args.get('date')
    if not selected_date:
        return jsonify({})

    appointment_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
    mechanics = Mechanic.query.all()
    slots = {}

    for m in mechanics:
        booked = Appointment.query.filter_by(mechanic_id=m.id, appointment_date=appointment_date).count()
        slots[m.id] = 4 - booked

    return jsonify(slots)

@app.route('/book', methods=['POST'])
def book():
    name = request.form['name']
    address = request.form['address']
    phone = request.form['phone']
    car_license = request.form['car_license']
    car_engine = request.form['car_engine']
    mechanic_id = int(request.form['mechanic'])
    appointment_date = datetime.strptime(request.form['appointment_date'], '%Y-%m-%d').date()

    existing = db.session.query(Appointment).join(Client).filter(
        Client.phone == phone,
        Appointment.appointment_date == appointment_date
    ).first()

    if existing:
        flash("You already have an appointment on this date.")
        return redirect(url_for('index'))

    count = Appointment.query.filter_by(mechanic_id=mechanic_id, appointment_date=appointment_date).count()
    if count >= 4:
        flash("Selected mechanic is fully booked for this date.")
        return redirect(url_for('index'))

    client = Client(name=name, address=address, phone=phone, car_license=car_license, car_engine=car_engine)
    db.session.add(client)
    db.session.commit()

    appointment = Appointment(client_id=client.id, mechanic_id=mechanic_id, appointment_date=appointment_date)
    db.session.add(appointment)
    db.session.commit()

    flash("Appointment booked successfully!")
    return redirect(url_for('index'))

@app.route('/admin')
def admin():
    if not session.get('logged_in'):
        flash('Please log in to access the admin panel.')
        return redirect(url_for('index'))
    
    appointments = Appointment.query.order_by(Appointment.appointment_date.desc()).all()
    mechanics = Mechanic.query.all()
    return render_template('admin.html', appointments=appointments, mechanics=mechanics)

@app.route('/admin/update/<int:appointment_id>', methods=['POST'])
def update_appointment(appointment_id):
    new_date = datetime.strptime(request.form['new_date'], '%Y-%m-%d').date()
    new_mechanic_id = int(request.form['new_mechanic'])

    appt = Appointment.query.get(appointment_id)

    count = Appointment.query.filter_by(mechanic_id=new_mechanic_id, appointment_date=new_date).count()
    if count >= 4:
        flash("Selected mechanic already has 4 appointments on this date.")
        return redirect(url_for('admin'))

    appt.appointment_date = new_date
    appt.mechanic_id = new_mechanic_id
    db.session.commit()
    flash("Appointment updated successfully.")
    return redirect(url_for('admin'))

@app.route('/admin_login', methods=['POST'])
def admin_login():
    password = request.form['admin_password']
    if password == 'admin123':  
        session['logged_in'] = True  # Mark the admin as logged in
        return redirect(url_for('admin'))
    else:
        flash('Wrong admin password!')
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)  # Remove 'logged_in' session variable
    flash('You have been logged out successfully!')
    return redirect(url_for('index'))


if __name__ == '__main__':
    with app.app_context():
        setup()
    app.run(debug=True)
