from flask import render_template, redirect, url_for, request, abort, flash
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
        return render_template("admin/users.html", users=users)
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
        flash("Пользователь изменён!", "success")
        return redirect(url_for("admin.admin_panel"))
    cursor = get_db().cursor()
    cursor.execute("select * from users where ID=?", (id,))
    data = cursor.fetchone()
    return render_template("admin/edit_user.html", datas=data)


@admin.route("/add_user_role/<string:id>", methods=["POST", "GET"])
@login_required
def add_user_role(id):
    if request.method == "POST":
        selected_values = request.form.getlist("check_box_roles")
        cursor = get_db().cursor()
        for value in selected_values:
            cursor.execute(
                "INSERT INTO links (role_id, user_id) VALUES (?,?)", (value, id)
            )
        cursor.connection.commit()
        flash("Роли добавлены!", "success")
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
@login_required
def delete_user_role(id):
    if request.method == "POST":
        selected_values = request.form.getlist("check_box_roles")
        cursor = get_db().cursor()
        for value in selected_values:
            cursor.execute(
                "DELETE from links where role_id=? and user_id=?", (value, id)
            )
        cursor.connection.commit()
        flash("Роли удалены!", "success")
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
@login_required
def delete_user(id):
    cursor = get_db().cursor()
    cursor.execute("delete from users where ID=?", (id,))
    cursor.connection.commit()
    flash("Пользователь удалён!", "success")
    return redirect(url_for("admin.admin_panel"))


@admin.route("/add_user", methods=["POST", "GET"])
@login_required
def add_user():
    if request.method == "POST":
        name = request.form["name"]
        password = request.form["password"]
        cursor = get_db().cursor()
        cursor.execute("SELECT * FROM users WHERE username= ?", (name,))
        user = cursor.fetchone()
        if user:
            flash("Пользователь с таким именем уже существует!", "error")
            return render_template("admin/add_user.html")
        hash_password = generate_password_hash(password, method="sha256")
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?,?)", (name, hash_password)
        )
        cursor.connection.commit()
        flash("Пользователь добавлен!", "success")
        return redirect(url_for("admin.admin_panel"))
    return render_template("admin/add_user.html")


@admin.route("/add_role", methods=["POST", "GET"])
@login_required
def add_role():
    if request.method == "POST":
        name = request.form["name"]
        cursor = get_db().cursor()
        cursor.execute("SELECT * FROM roles WHERE name= ?", (name,))
        role = cursor.fetchone()
        if role:
            flash("Роль с таким именем уже существует!", "error")
            return render_template("admin/add_role.html")
        cursor.execute("INSERT INTO roles (name) VALUES (?)", (name,))
        cursor.connection.commit()
        flash("Роль добавлена!", "success")
        return redirect(url_for("admin.admin_panel"))
    return render_template("admin/add_role.html")


@admin.route("/works")
@login_required
def works():
    if current_user.username == "admin":
        cursor = get_db().cursor()
        cursor.execute(
            """
        select 
            w.*
            ,tp.name tp_name
        from 
            works w
            join techprocesses tp on tp.id = w.techprocess_id
            """
        )
        works = cursor.fetchall()
        return render_template("admin/works.html", works=works)
    else:
        abort(403, "Отсутствует доступ к данной странице")


@admin.route("/edit_work/<string:id>", methods=["POST", "GET"])
@login_required
def edit_work(id):
    if request.method == "POST":
        cursor = get_db().cursor()
        workname = request.form["workname"]
        url = request.form["url"]
        techprocess_id = request.form["techprocess_select"]
        cursor.execute(
            "update works set name=?, url=?, techprocess_id=? where ID=?",
            (workname, url, int(techprocess_id), id),
        )
        cursor.connection.commit()
        flash("Вид работы изменен!", "success")
        return redirect(url_for("admin.works"))
    cursor = get_db().cursor()
    cursor.execute(
        """select w.*, tp.name tp_name from 
    works w
    join techprocesses tp on tp.id = w.techprocess_id
     where w.id=?
    """,
        (id,),
    )
    data = cursor.fetchone()
    techprocesses = cursor.execute("select * from techprocesses").fetchall()
    return render_template(
        "admin/edit_work.html", datas=data, techprocesses=techprocesses
    )


@admin.route("/delete_work/<string:id>", methods=["GET"])
@login_required
def delete_work(id):
    cursor = get_db().cursor()
    cursor.execute("delete from works where ID=?", (id,))
    cursor.connection.commit()
    flash("Вид работы удален!", "success")
    return redirect(url_for("admin.works"))


@admin.route("/add_work", methods=["POST", "GET"])
@login_required
def add_work():
    if request.method == "POST":
        name = request.form["workname"]
        url = request.form["url"]
        techprocess_id = request.form["techprocess_select"]
        cursor = get_db().cursor()
        cursor.execute("SELECT * FROM works WHERE url= ?", (url,))
        work = cursor.fetchone()
        if work:
            flash("Такой url уже существует!", "error")
            return render_template("admin/add_work.html")
        cursor.execute(
            "INSERT INTO works (name, url, techprocess_id) VALUES (?,?,?)",
            (
                name,
                url,
                techprocess_id,
            ),
        )
        cursor.connection.commit()
        flash("Вид работы добавлен!", "success")
        return redirect(url_for("admin.works"))

    cursor = get_db().cursor()
    techprocesses = cursor.execute("select * from techprocesses").fetchall()
    return render_template("admin/add_work.html", techprocesses=techprocesses)


@admin.route("/add_techprocess", methods=["POST", "GET"])
@login_required
def add_techprocess():
    if request.method == "POST":
        name = request.form["tp_name"]
        cursor = get_db().cursor()
        cursor.execute("SELECT * FROM techprocesses WHERE name= ?", (name,))
        techprocess = cursor.fetchone()
        if techprocess:
            flash("Техпроцесс с таким именем уже существует", "error")
            return render_template("admin/add_techprocess.html")
        cursor.execute("INSERT INTO techprocesses (name) VALUES (?)", (name,))
        cursor.connection.commit()
        flash("Техпроцесс добавлен!", "success")
        return redirect(url_for("admin.works"))
    return render_template("admin/add_techprocess.html")


@admin.route("/messages")
@login_required
def messages():
    if current_user.username == "admin":
        cursor = get_db().cursor()
        cursor.execute(
            """
        SELECT 
            m.*
            ,t.name tp_name
            ,w.name workname
        FROM 
            template_messages m
            join works w on m.work_id = w.id
            join techprocesses t on w.techprocess_id = t.id
        """
        )
        messages = cursor.fetchall()
        return render_template("admin/messages.html", messages=messages)
    else:
        abort(403, "Отсутствует доступ к данной странице")


@admin.route("/edit_message/<string:id>", methods=["POST", "GET"])
@login_required
def edit_message(id):
    if request.method == "POST":
        cursor = get_db().cursor()
        name = request.form["name"]
        template_message = request.form["template_message"]
        work_id = request.form["work_select"]
        cursor.execute(
            "update template_messages set name=?, template_message=?, work_id=? where ID=?",
            (name, template_message, int(work_id), id),
        )
        cursor.connection.commit()
        flash("Шаблон сообщений изменен!", "success")
        return redirect(url_for("admin.messages"))
    cursor = get_db().cursor()
    cursor.execute(
        """
        select 
            m.*
            ,w.name workname
        from 
            template_messages m
            join works w on w.id = m.work_id
        where
            m.id=?
    """,
        (id,),
    )
    data = cursor.fetchone()
    works = cursor.execute("select * from works").fetchall()

    return render_template("admin/edit_message.html", datas=data, works=works)


@admin.route("/delete_message/<string:id>", methods=["GET"])
@login_required
def delete_message(id):
    cursor = get_db().cursor()
    cursor.execute("delete from template_messages where ID=?", (id,))
    cursor.connection.commit()
    flash("Шаблон сообщений удален!", "success")
    return redirect(url_for("admin.messages"))


@admin.route("/add_message", methods=["POST", "GET"])
@login_required
def add_message():
    if request.method == "POST":
        name = request.form["name"]
        template_message = request.form["template_message"]
        work_id = request.form["work_select"]
        cursor = get_db().cursor()
        cursor.execute(
            """
        INSERT INTO template_messages (name, template_message, work_id)
         VALUES (?,?,?)""",
            (
                name,
                template_message,
                work_id,
            ),
        )
        cursor.connection.commit()
        flash("Шаблон сообщений добавлен!", "success")
        return redirect(url_for("admin.messages"))

    cursor = get_db().cursor()
    works = cursor.execute("select * from works").fetchall()
    return render_template("admin/add_message.html", works=works)


@admin.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
