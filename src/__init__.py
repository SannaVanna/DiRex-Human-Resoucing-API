from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .flasklogin import login_manager
from flask_cors import CORS
from .db import db
from src.routes.auth_routes import auth_bp
from src.routes.get_employee import get_employee_bp
from src.routes.post_employee import post_employee_bp
from src.routes.put_employee import put_employee_bp
from src.routes.delete_employee import delete_employee_bp


#app = Flask(__name__, static_folder="./templates/assets", static_url_path="/assets")
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///employee.db'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#db.init_app(app)
#migrate = Migrate(app, db)

#login_manager.init_app(app)
#login_manager.login_view = 'routes.login'

#CORS(app)

def createApp():
    app = Flask(__name__, static_folder="./templates/assets", static_url_path="/assets")
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///employee.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate = Migrate(app, db)

    login_manager.init_app(app)
    login_manager.login_view = 'routes.login'

    CORS(app)


    app.config['SECRET_KEY'] = 'humanresourcingemployeesecretkey'
    app.config['DEBUG'] = True
    app.register_blueprint(routes, url_prefix="/")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(get_employee_bp, url_prefix="/api")
    app.register_blueprint(post_employee_bp, url_prefix="/api")
    app.register_blueprint(put_employee_bp, url_prefix="/api")
    app.register_blueprint(delete_employee_bp, url_prefix="/api")   

    #home_view = Home.as_view('home_view')
    #app.add_url_rule('/', view_func=home_view, methods=['GET', 'POST'])
    #app.add_url_rule('/<int:id>', view_func=home_view, methods=['GET', 'PUT', 'DELETE'])
    # initialize DB/tables and default data
    try:
        from .routes import init_db
        with app.app_context():
            init_db()
    except Exception:
        pass
    return app
