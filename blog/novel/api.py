from . import novel_blueprint
from flask_restful import Resource, reqparse, Api
import re
from flask import abort, jsonify
import requests
from ..main.models import Book

"""
这里是个人网站的novel api
"""


novel_api = Api(novel_blueprint)


class SearchNovel(Resource):
    """
    web send post request
    server get request and return response
    """
    def __init__(self):
        super(SearchNovel, self).__init__()

    def get(self, keyword):
        r = requests.get("http://www.biquge5200.com/modules/article/search.php", params={"searchkey": keyword})
        r.encoding = r.apparent_encoding  # 转化为最佳编码
        book_message = re.compile('<td class="odd"><a href="(.*?)">(.*?)</a></td>.*?'
                                  '<td class="even"><a href="(.*?)" target="_blank"> (.*?)</a></td>.*?'
                                  '<td class="odd">(.*?)</td>.*?'
                                  '<td class="even">(.*?)</td>.*?'
                                  '<td class="odd" align="center">(.*?)</td>.*?'
                                  '<td class="even" align="center">(.*?)</td>', re.S)
        # 使用正则匹配相应字符串 re.DOTALL / re.S 使'.' 匹配任意字符，包括换行符
        items = book_message.findall(r.text)
        if items:
            # 异常处理
            for i in items:
                print(i)
            return jsonify(items)
        abort(404)


class BookCase(Resource):
    # 书架

    def get(self):
        books = Book.query.all()
        return books


class BookOperation(Resource):
    # 书架操作
    """
    {
        operation  in ['add', 'delete', 'move']
        book_name: book's name
    }
    """
    def __init__(self):
        # 这里写参数要求
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('operation', type=str, required=True)
        self.parser.add_argument('book_name', type=str, required=True)

    def post(self):
        # 接受参数 返回操作状态码
        args = self.parser.parse_args()
        if args['operation'] == 'add' and args['book_name']:
            # 加入书架
            pass
        elif args['operation'] == 'delete' and args['book_name']:
            # 移除书籍
            pass
        elif args['operation'] == 'move' and args['book_name']:
            # 移入养肥区
            pass
        else:
            abort(400)  # bad request


novel_api.add_resource(SearchNovel, '/api/v1/search/<string:keyword>')
