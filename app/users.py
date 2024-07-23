from flask_login import UserMixin
from app.db import get_db


class User(UserMixin):
    """
    Класс представляющий пользователей.
 
    Attributes:
        id (str): ID пользователя.
        username (str): Имя пользователя-логин.
        password (str): Пароль.
        roles (list): Список ролей.
    """
    users = {}

    def __init__(self, id: str, username: str, password: str, user_roles: list):
        """
        Инициализация пользователя.
 
        Parameters:
            id (str): ID пользователя.
            username (str): Имя пользователя-логин.
            password (str): Пароль.
            roles (list): Список ролей.
        """
        self.id = id
        self.password = password
        self.username = username
        self.roles = user_roles
        User.users.update({self.id: self})

    @staticmethod
    def get_user(username):
        cursor = get_db().cursor()
        cursor.execute("SELECT * FROM users WHERE username= ?", (username,))
        user = cursor.fetchone()
        if user:
            return user

    @staticmethod
    def get_user_roles(user_id):
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
            (user_id,),
        ).fetchall()

        return user_roles

    def __str__(self) -> str:
        return f"<Id: {self.id}, Username: {self.username}, Password: {self.password}, Roles: {', '.join(self.roles)}>"

    def __repr__(self) -> str:
        return self.__str__()
