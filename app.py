from flask import Flask
from models.model import db, create_admin
from controllers.controller import controller_bp

app = Flask(__name__)
app.secret_key = 'supersecretkey'  #   session secret key

#  Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#  Initialize DB
db.init_app(app)

#  Register Blueprint
app.register_blueprint(controller_bp)

#  Create DB tables and admin on first run
with app.app_context():
    db.create_all()
    create_admin()

#  Run the app
if __name__ == '__main__':
    app.run(debug=True)
