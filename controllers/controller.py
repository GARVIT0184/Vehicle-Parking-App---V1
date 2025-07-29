from flask import Blueprint, render_template, request, redirect, url_for, session
from models.model import db, User, ParkingLot, ParkingSpot, Reservation
from datetime import datetime
from collections import defaultdict
from werkzeug.security import generate_password_hash, check_password_hash

controller_bp = Blueprint('controller', __name__)

#  Home 
@controller_bp.route('/')
def home():
    return render_template('index.html')

#  Register 
@controller_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        role = request.form['role']

        existing_user = User.query.filter_by(username=uname).first()
        if existing_user:
            return render_template('register.html', error="User already exists")

        hashed_pwd = generate_password_hash(pwd)
        new_user = User(username=uname, password=hashed_pwd, role=role)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('controller.login'))

    return render_template('register.html')

#  Login 
@controller_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if not user:
            flash("User does not exist. Please register first.", "danger")
            return redirect(url_for('controller.register'))

        if check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role

            if user.role == 'admin':
                return redirect(url_for('controller.admin_dashboard'))
            else:
                return redirect(url_for('controller.user_dashboard'))
        else:
            flash("Incorrect password. Please try again.", "danger")
            return redirect(url_for('controller.login'))

    return render_template('login.html')
#  Logout 
@controller_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('controller.home'))

#  Admin Dashboard 
@controller_bp.route('/admin_dashboard')
def admin_dashboard():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('controller.login'))

    lots = ParkingLot.query.all()
    users = User.query.filter_by(role='user').all()

    lot_names = []
    available_spots = []
    occupied_spots = []

    for lot in lots:
        lot_names.append(lot.name)
        available = ParkingSpot.query.filter_by(lot_id=lot.id, status='A').count()
        occupied = ParkingSpot.query.filter_by(lot_id=lot.id, status='O').count()
        available_spots.append(available)
        occupied_spots.append(occupied)

    return render_template('admin_dashboard.html',
                           lots=lots, users=users,
                           lot_names=lot_names,
                           available_spots=available_spots,
                           occupied_spots=occupied_spots)

#  Add Parking Lot 
@controller_bp.route('/add_lot', methods=['GET', 'POST'])
def add_lot():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('controller.login'))

    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        pincode = request.form['pincode']
        price = float(request.form['price'])
        total_spots = int(request.form['total_spots'])

        lot = ParkingLot(name=name, address=address, pincode=pincode, price=price, total_spots=total_spots)
        db.session.add(lot)
        db.session.commit()

        for _ in range(total_spots):
            spot = ParkingSpot(lot_id=lot.id, status='A')
            db.session.add(spot)
        db.session.commit()

        return redirect(url_for('controller.admin_dashboard'))

    return render_template('add_lot.html')

#  Edit Parking Lot 
@controller_bp.route('/edit_lot/<int:lot_id>', methods=['GET', 'POST'])
def edit_lot(lot_id):
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('controller.login'))

    lot = ParkingLot.query.get_or_404(lot_id)

    if request.method == 'POST':
        lot.name = request.form['name']
        lot.address = request.form['address']
        lot.pincode = request.form['pincode']
        lot.price = float(request.form['price'])
        db.session.commit()
        return redirect(url_for('controller.admin_dashboard'))

    return render_template('edit_lot.html', lot=lot)

# Delete Parking Lot
@controller_bp.route('/delete_lot/<int:lot_id>')
def delete_lot(lot_id):
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('controller.login'))

    lot = ParkingLot.query.get_or_404(lot_id)
    spots = ParkingSpot.query.filter_by(lot_id=lot.id).all()

    if any(spot.status == 'O' for spot in spots):
        return "Cannot delete lot with occupied spots."

    for spot in spots:
        db.session.delete(spot)
    db.session.delete(lot)
    db.session.commit()
    return redirect(url_for('controller.admin_dashboard'))

#  User Dashboard 
@controller_bp.route('/dashboard')
def user_dashboard():
    if 'role' not in session or session['role'] != 'user':
        return redirect(url_for('controller.login'))

    user_id = session['user_id']
    user = User.query.get(user_id)

    active_reservation = Reservation.query.filter_by(user_id=user_id, end_time=None).first()

    return render_template('user_dashboard.html',
                           user=user,
                           active_reservation=active_reservation)

#  Book Parking 
@controller_bp.route('/book_parking', methods=['GET', 'POST'])
def book_parking():
    if 'role' not in session or session['role'] != 'user':
        return redirect(url_for('controller.login'))

    lots = []
    if request.method == 'POST':
        pincode = request.form.get('pincode')
        lots = ParkingLot.query.filter_by(pincode=pincode).all()

    return render_template('book_parking.html', lots=lots)

@controller_bp.route('/book_spot/<int:lot_id>')
def book_spot(lot_id):
    if 'role' not in session or session['role'] != 'user':
        return redirect(url_for('controller.login'))

    spot = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').first()

    if spot:
        spot.status = 'O'
        reservation = Reservation(
            spot_id=spot.id,
            user_id=session['user_id'],
            start_time=datetime.now()
        )
        db.session.add(reservation)
        db.session.commit()
        return redirect(url_for('controller.user_dashboard'))

    return "No available spots in this lot", 404

#  Release Spot
@controller_bp.route('/release_spot', methods=['POST'])
def release_spot():
    if 'role' not in session or session['role'] != 'user':
        return redirect(url_for('controller.login'))

    reservation_id = request.form.get('reservation_id')
    reservation = Reservation.query.get(reservation_id)

    if reservation and not reservation.end_time:
        reservation.end_time = datetime.now()
        duration = (reservation.end_time - reservation.start_time).total_seconds() / 3600
        reservation.cost = round(duration * reservation.spot.lot.price, 2)
        reservation.spot.status = 'A'
        db.session.commit()

    return redirect(url_for('controller.user_dashboard'))

#  User Summary 
@controller_bp.route('/user/summary')
def user_summary():
    if 'role' not in session or session['role'] != 'user':
        return redirect(url_for('controller.login'))

    user_id = session['user_id']
    bookings = Reservation.query.filter_by(user_id=user_id).all()

    lot_durations = defaultdict(float)
    for res in bookings:
        if res.end_time:
            duration = (res.end_time - res.start_time).total_seconds() / 3600
            lot_name = res.spot.lot.name
            lot_durations[lot_name] += round(duration, 1)

    lot_names = list(lot_durations.keys())
    lot_hours = list(lot_durations.values())

    return render_template('user_summary.html', lot_names=lot_names, lot_hours=lot_hours)

#  User History 
@controller_bp.route('/user/history')
def user_history():
    if 'role' not in session or session['role'] != 'user':
        return redirect(url_for('controller.login'))

    reservations = Reservation.query.filter_by(user_id=session['user_id']).all()
    return render_template('user_history.html', reservations=reservations)
@controller_bp.route('/add_spots/<int:lot_id>')
def add_spots(lot_id):
    return f"Add Spots UI for lot ID {lot_id}"
