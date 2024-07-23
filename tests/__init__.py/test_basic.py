import unittest
from app import create_app


class BasicTestCase(unittest.TestCase):

    def setUp(self):
        app_resender = create_app('testing')
        self.app = app_resender.test_client()

    def login(self, username, password):
        return self.app.post('/auth/login', data=dict(
            name=username,
            password=password
        ), follow_redirects=True
                             )

    def logout(self):
        return self.app.get('/auth/logout', follow_redirects=True)

    def test_main_page(self):
        rv = self.app.get('/')
        assert 'Лёгкие и доступные переотправки туда-сюда' in rv.data.decode('utf-8')

    def test_login_logout(self):
        rv = self.login('netrebin', 'netrebin')
        assert 'Добро пожаловать' in rv.data.decode('utf-8')

        rv = self.logout()
        assert 'Лёгкие и доступные переотправки туда-сюда' in rv.data.decode('utf-8')

        rv = self.login('netrebin', 'netrebin2')
        assert 'Пожалуйста, проверьте вводимые данные' in rv.data.decode('utf-8')

        rv = self.login('netrebin2', 'netrebin')
        assert 'Пользователь не найден' in rv.data.decode('utf-8')

    def test_admin_panel(self):
        rv = self.login('netrebin', 'netrebin')
        assert 'Добро пожаловать' in rv.data.decode('utf-8')

        rv = self.app.get('/admin/admin_panel')
        assert 'Отсутствует доступ к данной странице' in rv.data.decode('utf-8')

        rv = self.logout()
        assert 'Лёгкие и доступные переотправки туда-сюда' in rv.data.decode('utf-8')

        rv = self.login('admin', 'admin')
        assert 'Добро пожаловать' in rv.data.decode('utf-8')

        rv = self.app.get('/admin/admin_panel')
        assert 'Привет, Админ' in rv.data.decode('utf-8')


if __name__ == '__main__':
    unittest.main()
