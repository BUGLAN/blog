# unit test

import unittest
import pymysql
import sys
from blog import create_app
from config import TestingConfig
from flask import current_app
from extensions import db

sys.path.append('..')


def create_db():
    conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', charset='utf8')
    cursor = conn.cursor()
    cursor.execute('show databases')
    databases = cursor.fetchall()
    db_name = 'blog_test'
    if [database for database in databases if database[0] == 'blog_test']:
        cursor.execute('drop database if exists %s;' % db_name)
    else:
        cursor.execute('create database if not exists %s charset=utf8;' % db_name)
    conn.commit()
    conn.close()


def drop_db():
    conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', charset='utf8')
    cursor = conn.cursor()
    cursor.execute('show databases')
    databases = cursor.fetchall()
    db_name = 'blog_test'
    if [database for database in databases if database[0] == 'blog_test']:
        cursor.execute('drop database if exists %s;' % db_name)
    conn.commit()
    conn.close()


class MainViewsTest(unittest.TestCase):

    def setUp(self):
        """
        1. create db if not exists, drop db and create if exists
        2. db.create_all()
        """
        create_db()
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.test_client = self.app.test_client()
        db.create_all()

    def tearDown(self):
        """
        1. drop db if exists
        """
        drop_db()
        self.app_context.pop()

    def test_exists_app(self):
        self.assertFalse(current_app is None)
