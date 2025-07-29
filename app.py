from flask import Flask
from models.model import db, User
from controllers.controller import controller_bp
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Secret key for sessions

# Database Configuration 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize DB
db.init_app(app)

#  Register Blueprints 
app.register_blueprint(controller_bp)

#  Create DB Tables and Default Admin
with app.app_context():
    db.create_all()

    # Create a default admin user if not already present
    if not User.query.filter_by(username='admin').first():
        admin_user = User(
            username='admin',
            password=generate_password_hash('admin123'),  # Default password
            role='admin'
        )
        db.session.add(admin_user)
        db.session.commit()
        print("✅ Default admin user created: admin/admin123")
    else:
        print("ℹ️ Admin user already exists.")

#  Run the App 
if __name__ == '__main__':
    app.run(debug=True)
