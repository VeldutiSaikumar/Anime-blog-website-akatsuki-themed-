from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from ..forms import PostForm
from ..models import Post
from ..extensions import db
from ..utils import upload_image

posts_bp = Blueprint('posts', __name__, url_prefix='/post')

@posts_bp.route('/new', methods=['GET','POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        image_url = None
        if form.image.data:
            image_url = upload_image(form.image.data, folder='naruto_posts')
        post = Post(title=form.title.data, body=form.body.data, image_url=image_url, author_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        flash('Post created!', 'success')
        return redirect(url_for('index'))
    return render_template('new_post.html', form=form)

@posts_bp.route('/<int:post_id>')
def detail(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', post=post)

@posts_bp.route('/<int:post_id>/edit', methods=['GET','POST'])
@login_required
def edit(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author_id != current_user.id:
        flash('You do not have permission to edit this post.', 'danger')
        return redirect(url_for('posts.detail', post_id=post.id))
    form = PostForm(obj=post)
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        if form.image.data:
            post.image_url = upload_image(form.image.data, folder='naruto_posts')
        db.session.commit()
        flash('Post updated.', 'success')
        return redirect(url_for('posts.detail', post_id=post.id))
    return render_template('edit_post.html', form=form, post=post)

@posts_bp.route('/<int:post_id>/delete', methods=['POST'])
@login_required
def delete(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author_id != current_user.id:
        flash('You do not have permission to delete this post.', 'danger')
        return redirect(url_for('posts.detail', post_id=post.id))
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted.', 'info')
    return redirect(url_for('index'))
