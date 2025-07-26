from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(120))
    role = db.Column(db.String(10))  # 'admin' or 'user'

    reservations = db.relationship('Reservation', backref='user')

class ParkingLot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    address = db.Column(db.String(200))
    pincode = db.Column(db.String(10))
    price = db.Column(db.Float)
    total_spots = db.Column(db.Integer)

    spots = db.relationship('ParkingSpot', backref='lot')

class ParkingSpot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'))
    status = db.Column(db.String(1))  # 'A' = Available, 'O' = Occupied

    reservations = db.relationship('Reservation', backref='spot')

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime, nullable=True)
    cost = db.Column(db.Float, nullable=True)

def create_admin():
    existing = User.query.filter_by(username='Garvit', role='admin').first()
    if not existing:
        admin = User(username='Garvit', password='niCk2013', role='admin')
        db.session.add(admin)
        db.session.commit()

