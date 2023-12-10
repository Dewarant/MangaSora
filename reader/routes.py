import os, secrets
from reader import app, db
from reader.models import Book, Users
from flask import render_template, send_from_directory, request, flash, url_for, redirect
from PIL import Image
from reader.forms import BookForm, UpdateBook
from sqlalchemy.exc import IntegrityError
from flask_login import login_user, login_required, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    books = Book.query.order_by(Book.created_at.desc()).paginate(page=page, per_page=4)
    return render_template('index.html', books=books)

@app.route('/news')
def news():
    return render_template("news.html")
@app.route('/uploads/<filename>')
def send_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)    

@app.route('/<int:book_id>/')
def book(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('book.html', book=book)

@app.route('/best/')
def best():
    page = request.args.get('page', 1, type=int)
    books = Book.query.filter(Book.rating > 4).paginate(page=page, per_page=4)
    return render_template('best.html', books=books)      

def save_picture(cover):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(cover.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], picture_fn)

    output_size = (220, 340)
    i = Image.open(cover)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

@app.route('/create/', methods=('GET', 'POST'))
@login_required
def create():
    form = BookForm()
    if form.validate_on_submit():
        if form.cover.data:
            cover = save_picture(form.cover.data)
        else:
            cover ='default.jpg'   
        title = form.title.data
        author = form.author.data
        genre = form.genre.data
        rating = int(form.rating.data)
        description = form.description.data
        notes = form.notes.data
        price = form.price.data
        book = Book(title=title,
            author=author,
            genre=genre,
            rating=rating,
            cover=cover,
            description=description,
            notes=notes,
            price=price)
        db.session.add(book)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('create.html', form=form)

@app.route('/<int:book_id>/edit/', methods=('GET', 'POST'))
@login_required
def edit(book_id):
    book = Book.query.get_or_404(book_id)
    form = UpdateBook()
    if form.validate_on_submit():
        if form.cover.data:
            cover = save_picture(form.cover.data)
        else:
            cover = book.cover
        book.title = form.title.data
        book.author = form.author.data
        book.genre = form.genre.data
        book.rating = int(form.rating.data)
        book.description = form.description.data
        book.notes = form.notes.data
        book.price = form.price.data
        try:
            db.session.commit()
            return redirect(url_for('index'))
        except IntegrityError:
            db.session.rollback()
            flash('Произошла ошибка: такая манга уже есть в базе', 'error')
            return render_template('edit.html', form=form)
      
            
    elif request.method == 'GET':
        form.title.data = book.title
        form.author.data = book.author
        form.genre.data = book.genre
        form.rating.data = book.rating
        form.cover.data = book.cover
        form.description.data = book.description
        form.notes.data = book.notes
        form.price.data = book.price

    return render_template('edit.html', form=form)      

@app.post('/<int:book_id>/delete/')
@login_required
def delete(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    return redirect(url_for('index'))    



@app.route('/about')
def about():
    return render_template("about.html")
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    login = request.form.get('email')
    password = request.form.get('password')

    if login and password:
        user = Users.query.filter_by(email=login).first()

        if user and check_password_hash(user.psw, password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page)

        else:
            flash('Неверный логин или пароль')
    else:
        flash('Заполните логин или пароль')
    return render_template("login.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    login = request.form.get('email')
    password = request.form.get('password')
    password2 = request.form.get('password2')

    if request.method == 'POST':
        if not (login or password or password2):
            flash('Заполните ячейки')
        elif password != password2:
            flash('Пароли не совпадают')
        else:
            hesh_pwd = generate_password_hash(password)
            new_user = Users(email=login, psw=hesh_pwd)
            db.session.add(new_user)
            db.session.commit()
            return redirect('login')
    return render_template("register.html")


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login_page'))


@app.after_request
def redirect_to_singlin(response):
    if response.status_code == 401:
        return redirect(url_for('login_page') + '?next=' + request.url)
    return response
