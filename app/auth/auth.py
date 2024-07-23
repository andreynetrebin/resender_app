from flask import render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from app.db import get_db
from flask import Blueprint
from flask_login import login_user, logout_user, login_required
from ..users import User

auth = Blueprint("auth", __name__)


@auth.route("/login")
def login():
    """ 
    Форма авторизации.

    Parameters:
        GET:/login
        
    Returns:
        Рендеринг шаблона main/login.html.

    """
    return render_template("main/login.html")


@auth.route("/signup")
def signup():
    """ 
    Регистрация пользователей.

    Parameters:
        GET:/signup

    Returns:
        Рендеринг шаблона main/signup.html.

    """
    return render_template("main/signup.html")


@auth.route("/signup", methods=["POST"])
def signup_post():
    """ 
    Регистрация пользователей.

    Parameters:
        POST:/signup

    Returns:
        При успехе редирект на страницу авторизации, при неуспехе на страницу регистрации.

    """
    name = request.form.get("name")
    password = request.form.get("password")
    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM users WHERE username= ?", (name,))
    user = cursor.fetchone()
    if user:
        flash("Пользователь с таким именем уже существует")
        return redirect(url_for("auth.signup"))
    hash_password = generate_password_hash(password, method="sha256")
    cursor.execute(
        "INSERT INTO users (username, password) VALUES (?,?)", (name, hash_password)
    )
    cursor.connection.commit()

    return redirect(url_for("auth.login"))


@auth.route("/logout")
@login_required
def logout():
    """ 
    Выход пользователя.

    Parameters:
        GET:/logout

    Returns:
        Редирект на главную страницу.

    """

    logout_user()
    return redirect(url_for("main.index"))


@auth.route("/login", methods=["POST"])
def login_post():
    """ 
    Авторизация пользователей.

    Parameters:
        POST:/login

    Returns:
        При успехе редирект на страницу переотправок, при неуспехе на страницу авторизации.

    """
    name = request.form.get("name")
    password = request.form.get("password")
    remember = True if request.form.get("remember") else False
    db_user = User.get_user(name)
    if db_user:
        user_roles = [item["name"] for item in User.get_user_roles(db_user[0])]
        user = User(db_user[0], db_user[1], db_user[2], user_roles)

        if check_password_hash(user.password, password):
            login_user(user, remember=remember)
            return redirect(url_for("resend.index"))

        else:
            flash("Пожалуйста, проверьте вводимые данные")
            return redirect(
                url_for("auth.login")
            )
    else:
        flash("Пользователь не найден")
        return redirect(
            url_for("auth.login")
        )
