from flask import render_template, redirect, url_for, request, flash, session, abort
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint
from flask_login import login_required, current_user
from app.db import get_db

profile = Blueprint(
    "profile", __name__, template_folder="templates", static_folder="static"
)


@profile.route("/")
@login_required
def user_profile():
    """ 
    Главная страцица.

    Parameters:
        GET:/profile

    Returns:
        Рендеринг шаблона profile/profile.html.

    """
    return render_template("profile/profile.html")


@profile.route("/change_password", methods=["POST", "GET"])
@login_required
def change_password():
    if request.method == "POST":
        new_password = request.form["new_password"]

        if check_password_hash(current_user.password, new_password):
            flash("Пароль совпадает со старым, пожалуйста придумайте другой")
            return render_template("profile/change_password.html")
        else:
            cursor = get_db().cursor()
            hash_password = generate_password_hash(new_password, method="sha256")
            cursor.execute(
                "update users set PASSWORD=? where ID=?",
                (hash_password, current_user.id), )
            cursor.connection.commit()

            return redirect(url_for("profile.user_profile"))

        return render_template("profile/change_password.html")

    return render_template("profile/change_password.html")
