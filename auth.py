from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from ..forms import RegistrationForm, LoginForm, RequestResetForm, ResetPasswordForm
from ..models import User
from ..extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user, login_required
from ..utils import generate_token, confirm_token, send_email
from flask import render_template_string

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password=hashed, is_confirmed=False)
        db.session.add(user)
        db.session.commit()
        token = generate_token(user.email)
        confirm_url = url_for('auth.confirm_email', token=token, _external=True)
        html = render_template('email/activate.html', confirm_url=confirm_url, user=user)
        send_email("Confirm your Naruto Blog account", [user.email], html)
        flash('A confirmation email has been sent. Please check your inbox.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

@auth_bp.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = confirm_token(token)
    except Exception:
        flash('The confirmation link is invalid or has expired.', 'danger')
        return redirect(url_for('index'))
    user = User.query.filter_by(email=email).first_or_404()
    if user.is_confirmed:
        flash('Account already confirmed. Please login.', 'success')
    else:
        user.is_confirmed = True
        db.session.commit()
        flash('You have confirmed your account. Thanks!', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            if not user.is_confirmed:
                flash('Please confirm your email address first.', 'warning')
                return redirect(url_for('auth.login'))
            login_user(user, remember=form.remember.data)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('index'))
        flash('Invalid credentials.', 'danger')
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# Password reset
@auth_bp.route('/reset_password_request', methods=['GET','POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = generate_token(user.email, salt='password-reset')
            reset_url = url_for('auth.reset_token', token=token, _external=True)
            html = render_template('email/reset_password.html', reset_url=reset_url, user=user)
            send_email('Password Reset Request', [user.email], html)
            flash('An email with password reset instructions has been sent if the email exists.', 'info')
        else:
            flash('If that email exists, a reset link will be sent.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('reset_request.html', form=form)

@auth_bp.route('/reset/<token>', methods=['GET','POST'])
def reset_token(token):
    try:
        email = confirm_token(token, salt='password-reset', expiration=current_app.config.get('EMAIL_TOKEN_EXPIRATION'))
    except Exception:
        flash('The reset link is invalid or has expired.', 'danger')
        return redirect(url_for('auth.reset_request'))
    user = User.query.filter_by(email=email).first_or_404()
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password = generate_password_hash(form.password.data)
        db.session.commit()
        flash('Your password has been updated. You can now login.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('reset_token.html', form=form)
