import os
from flask import Flask, render_template
from .extensions import db, login_manager, mail
from .config import Config
from cloudinary import config as cloud_config
from .models import User 
from flask_login import current_user

def create_app():
    from flask_login import current_user
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object(Config)

    # initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    login_manager.login_view = 'auth.login'      # redirect here if @login_required
    login_manager.login_message_category = 'info'
    def inject_user():
        return dict(current_user=current_user)


    # configure cloudinary
    cloud_config(
        cloud_name=app.config.get('CLOUDINARY_CLOUD_NAME'),
        api_key=app.config.get('CLOUDINARY_API_KEY'),
        api_secret=app.config.get('CLOUDINARY_API_SECRET'),
        secure=True
    )

    # blueprints / routes
    from .routes.auth import auth_bp
    from .routes.posts import posts_bp
    from .routes.users import users_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(posts_bp)
    app.register_blueprint(users_bp)

    @app.route('/')
    def index():
        from .models import Post
        posts = Post.query.order_by(Post.created_at.desc()).all()
        return render_template('index.html', posts=posts)

    return app
