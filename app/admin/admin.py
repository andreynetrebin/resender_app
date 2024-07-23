from flask import render_template, redirect, url_for, request, abort
from werkzeug.security import generate_password_hash
from app.db import get_db
from flask import Blueprint
from flask_login import logout_user, login_required, current_user

admin = Blueprint(
    "admin", __name__, template_folder="templates", static_folder="static"
)


@admin.route("/admin_panel")
@login_required
def admin_panel():
    if current_user.username == "admin":
        cursor = get_db().cursor()
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        # Загрузка и отображение админ-панели
        return render_template("admin/admin_panel.html", users=users)
    else:
        abort(403, "Отсутствует доступ к данной странице")


@admin.route("/edit_user/<string:id>", methods=["POST", "GET"])
def edit_user(id):
    if request.method == "POST":
        cursor = get_db().cursor()
        username = request.form["username"]
        password = request.form["password"]
        hash_password = generate_password_hash(password, method="sha256")
        cursor.execute(
            "update users set USERNAME=?, PASSWORD=? where ID=?",
            (username, hash_password, id),
        )
        cursor.connection.commit()
        # flash('User Updated','success')
        return redirect(url_for("admin.admin_panel"))
    cursor = get_db().cursor()
    cursor.execute("select * from users where ID=?", (id,))
    data = cursor.fetchone()
    return render_template("admin/edit_user.html", datas=data)


@admin.route("/add_user_role/<string:id>", methods=["POST", "GET"])
def add_user_role(id):
    if request.method == "POST":
        selected_values = request.form.getlist("check_box_roles")
        cursor = get_db().cursor()
        for value in selected_values:
            cursor.execute(
                "INSERT INTO links (role_id, user_id) VALUES (?,?)", (value, id)
            )
        cursor.connection.commit()
        return redirect(url_for("admin.admin_panel"))

    cursor = get_db().cursor()
    user_roles = cursor.execute(
        """
        select 
            roles.name
        from
        users
            join links on users.id = links.user_id
            join roles on links.role_id = roles.id
        where users.id = ?    
        """,
        (id,),
    ).fetchall()
    all_roles = cursor.execute(
        """
    SELECT id, name FROM roles
    where id not in
    (select role_id from links where user_id = ?)""",
        (id,),
    ).fetchall()

    data = {"id": id, "user_roles": user_roles, "all_roles": all_roles}

    return render_template("admin/add_user_role.html", data=data)


@admin.route("/delete_user_role/<string:id>", methods=["POST", "GET"])
def delete_user_role(id):
    if request.method == "POST":
        selected_values = request.form.getlist("check_box_roles")
        cursor = get_db().cursor()
        print(selected_values)
        for value in selected_values:
            cursor.execute(
                "DELETE from links where role_id=? and user_id=?", (value, id)
            )
        cursor.connection.commit()
        return redirect(url_for("admin.admin_panel"))

    cursor = get_db().cursor()
    user_roles = cursor.execute(
        """
        select 
            roles.id
            ,roles.name
        from
        users
            join links on users.id = links.user_id
            join roles on links.role_id = roles.id
        where users.id = ?    
        """,
        (id,),
    ).fetchall()
    data = {"id": id, "user_roles": user_roles}

    return render_template("admin/delete_user_role.html", data=data)


@admin.route("/delete_user/<string:id>", methods=["GET"])
def delete_user(id):
    cursor = get_db().cursor()
    cursor.execute("delete from users where ID=?", (id,))
    cursor.connection.commit()
    return redirect(url_for("admin.admin_panel"))


@admin.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@admin.route("/add_user", methods=["POST", "GET"])
def add_user():
    if request.method == "POST":
        name = request.form["uname"]
        password = request.form["contact"]
        cursor = get_db().cursor()
        cursor.execute("SELECT * FROM users WHERE username= ?", (name,))
        user = cursor.fetchone()
        if user:
            render_template("admin/add_user.html")
        hash_password = generate_password_hash(password, method="sha256")
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?,?)", (name, hash_password)
        )
        cursor.connection.commit()
        return redirect(url_for("admin.admin_panel"))
    return render_template("admin/add_user.html")


@admin.route("/add_role", methods=["POST", "GET"])
def add_role():
    if request.method == "POST":
        name = request.form["uname"]
        cursor = get_db().cursor()
        cursor.execute("SELECT * FROM roles WHERE name= ?", (name,))
        role = cursor.fetchone()
        if role:
            render_template("admin/add_role.html")
        cursor.execute("INSERT INTO roles (name) VALUES (?)", (name,))
        cursor.connection.commit()
        return redirect(url_for("admin.admin_panel"))
    return render_template("admin/add_role.html")
