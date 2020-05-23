import unittest

from blog.main.models import Role, Post, User, Category, Tag
from tests.test_app import create_db, drop_db, create_app, TestingConfig, db


class BlogClientTest(unittest.TestCase):

    def setUp(self):
        create_db()
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.test_client = self.app.test_client()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        drop_db()
        self.app_context.pop()

    def test_index_func_without_posts(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_data(as_text=True))
        response = self.client.get('/posts')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_data(as_text=True))

    def test_int_func_with_posts(self):
        post = Post()
        post.title = 'this is a test'
        post.text = 'test test' * 20
        db.session.add(post)
        db.session.commit()
        response = self.client.get('/')
        self.assertTrue(response.status_code, 200)
        self.assertTrue('this is a test' in response.get_data(as_text=True))
        response = self.client.get('/posts')
        self.assertTrue(response.status_code, 200)
        self.assertTrue('this is a test' in response.get_data(as_text=True))

    def test_login_get(self):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('登录' in response.get_data(as_text=True))

    def test_login_post_username(self):
        user = User()
        user.username = 'test for login'
        user.password = '123456'
        user.email = '123@123.com'
        db.session.add(user)
        db.session.commit()
        response = self.client.post('/login', data={'username': 'test for login',
                                                    'password': '123456'},
                                    follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('BUGLAN的个人小站' in response.get_data(as_text=True))

    def test_login_post_email(self):
        user = User()
        user.username = 'test for login'
        user.password = '123456'
        user.email = '123@123.com'
        db.session.add(user)
        db.session.commit()
        response = self.client.post('/login', data={'username': '123@123.com',
                                                    'password': '123456'},
                                    follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('BUGLAN的个人小站' in response.get_data(as_text=True))

    def test_post_error(self):
        user = User()
        user.username = 'test for login'
        user.email = '123@123.com'
        user.password = '123456'
        db.session.add(user)
        db.session.commit()
        response = self.client.post('/login', data={'username': '123@123.com',
                                                    'password': '12345'},
                                    follow_redirects=True)
        self.assertEqual(response.status_code, 404)

    def test_my_posts_without_login(self):
        response = self.client.get('/my_posts')
        self.assertEqual(response.status_code, 302)

    def test_my_posts_with_login(self):
        user = User()
        user.username = 'test for login'
        user.password = '123456'
        user.email = '123@123.com'
        db.session.add(user)
        db.session.commit()
        post = Post()
        post.title = 'this is a test'
        post.text = 'test test' * 20
        post.users = user
        db.session.add(post)
        db.session.commit()
        self.client.post('/login', data={'username': '123@123.com',
                                         'password': '123456'},
                         follow_redirects=True)
        response = self.client.get('/my_posts')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('this is a test' in response.get_data(as_text=True))

    def test_register_get(self):
        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('注册' in response.get_data(as_text=True))

    def test_register_post_error(self):
        response = self.client.post('/register', data={'username': 'test for login',
                                                       'email': '123@123.com',
                                                       'password1': '12345',
                                                       'password2': '123456'})
        self.assertEqual(response.status_code, 403)
        user = User()
        user.username = 'test for login'
        db.session.add(user)
        db.session.commit()
        response = self.client.post('/register', data={'username': 'test for login',
                                                       'email': '123@123.com',
                                                       'password1': '123456',
                                                       'password2': '123456'})
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.get_data(as_text=True) == '密码或用户名已被他人所占用')

    def test_register_post_success(self):
        response = self.client.post('/register', data={'username': 'test for login',
                                                       'email': '123@123.com',
                                                       'password1': '123456',
                                                       'password2': '123456'},
                                    follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('test for login' in response.get_data(as_text=True))

    def test_logout_get(self):
        response = self.client.get('/logout')
        self.assertEqual(response.status_code, 302)
        self.assertTrue('BUGLAN的个人小站' not in response.get_data(as_text=True))
        user = User()
        user.username = 'test for login'
        user.password = '123456'
        db.session.add(user)
        db.session.commit()
        self.client.post('/login', data={'username': 'test for login',
                                         'password': '123456'})
        response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('BUGLAN的个人小站' in response.get_data(as_text=True))

    def test_detail_get(self):
        post = Post()
        post.title = 'this is a test'
        post.text = 'test ' * 20
        db.session.add(post)
        db.session.commit()
        response = self.client.get('/post/1/detail')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('this is a test' in response.get_data(as_text=True))
        self.assertTrue('test ' * 20 in response.get_data(as_text=True))

    def test_detail_post(self):
        post = Post()
        post.title = 'this is a test'
        post.text = 'test ' * 20
        db.session.add(post)
        db.session.commit()
        response = self.client.post('/post/1/detail')
        self.assertEqual(response.status_code, 302)
        user = User()
        user.username = 'test for login'
        user.password = '123456'
        db.session.add(user)
        db.session.commit()
        self.client.post('/login', data={'username': 'test for login',
                                         'password': '123456'})
        response = self.client.post('/post/1/detail', data={'comment': ''}, follow_redirects=True)
        self.assertEqual(response.status_code, 403)
        self.assertTrue('评论不能为空' == response.get_data(as_text=True))
        response = self.client.post('/post/1/detail', data={'comment': 'comment for test'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('comment for test' in response.get_data(as_text=True))

    def test_reply_comment_get(self):
        response = self.client.get('/post/1/reply-comment')
        self.assertEqual(response.status_code, 405)

    def test_reply_comment_post(self):
        post = Post()
        post.title = 'this is a test'
        post.text = 'test ' * 20
        db.session.add(post)
        db.session.commit()
        user = User()
        user.username = 'test for login'
        user.password = '123456'
        db.session.add(user)
        db.session.commit()
        response = self.client.post('/post/1/reply-comment', data={'post_id': 1, 'content': 'reply-comment for test',
                                                                   'comment_id': 1}, follow_redirects=True)
        self.assertTrue(response.status_code, 302)
        self.client.post('/login', data={'username': 'test for login',
                                         'password': '123456'})

        self.client.post('/post/1/detail', data={'comment': 'comment for test'})
        response = self.client.post('/post/1/reply-comment', data={'post_id': 1, 'content': 'reply-comment for test',
                                                                   'comment_id': 1}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('reply-comment' in response.get_data(as_text=True))

    def test_show_category(self):
        category = Category()
        category.name = 'test'
        db.session.add(category)
        db.session.commit()
        post = Post()
        post.title = 'this is a test'
        post.text = 'test ' * 20
        post.category = category
        db.session.add(post)
        db.session.commit()

        response = self.client.get('/category/test/1')
        self.assertTrue('test' in response.get_data(as_text=True))
        self.assertTrue('this is a test' in response.get_data(as_text=True))

    def test_show_tag(self):
        tag = Tag()
        tag.name = 'test'
        db.session.add(tag)
        db.session.commit()
        post = Post()
        post.title = 'this is a test'
        post.text = 'test ' * 20
        post.tags.append(tag)
        db.session.add(post)
        db.session.commit()
        response = self.client.get('/tag/test/1')
        self.assertTrue('test' in response.get_data(as_text=True))
        self.assertTrue('this is a test' in response.get_data(as_text=True))

    def test_github_login(self):
        response = self.client.get('/github')
        self.assertEqual(response.status_code, 302)
        # 逻辑并不清晰
        # 需要模拟github登录 回调
        # 以后再搞
