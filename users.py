from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from ..forms import EditProfileForm
from ..models import User, Post
from ..extensions import db
from ..utils import upload_image
from werkzeug.security import generate_password_hash

users_bp = Blueprint('users', __name__, url_prefix='/user')

@users_bp.route('/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author_id=user.id).order_by(Post.created_at.desc()).all()
    return render_template('profile.html', user=user, posts=posts)

@users_bp.route('/edit', methods=['GET','POST'])
@login_required
def edit_profile():
    form = EditProfileForm(obj=current_user)
    if form.validate_on_submit():
        # username change check
        if form.username.data != current_user.username:
            if User.query.filter_by(username=form.username.data).first():
                flash('Username already taken.', 'danger')
                return redirect(url_for('users.edit_profile'))
            current_user.username = form.username.data
        current_user.bio = form.bio.data
        if form.avatar.data:
            current_user.avatar_url = upload_image(form.avatar.data, folder='naruto_avatars')
        db.session.commit()
        flash('Profile updated.', 'success')
        return redirect(url_for('users.profile', username=current_user.username))
    return render_template('edit_profile.html', form=form)
