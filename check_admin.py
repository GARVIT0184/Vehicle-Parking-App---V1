from models.model import db, User
from app import app

with app.app_context():
    admin = User.query.filter_by(username='Garvit', role='admin').first()

    if admin:
        print(" Admin already exists:", admin.username)
    else:
        new_admin = User(username='Garvit', password='niCk2013', role='admin')
        db.session.add(new_admin)
        db.session.commit()
        print(" Admin created successfully.")
