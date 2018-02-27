from . import novel_blueprint
from flask import render_template, request, redirect, url_for
from .spider import Spider
from blog.main.models import Book
from extensions import db
import sqlalchemy


@novel_blueprint.route('/novel/search')
def search():
    keyword = request.args.get('keyword')
    items = Spider.search(keyword)
    if items:
        return render_template('novel/search.html', items=items)
    elif items == "连接错误":
        return "连接错误"
    return render_template('novel/search.html')


@novel_blueprint.route('/novel/<key_url>/')
def novel_chapters(key_url):
    full_url = "http://www.biquge5200.com/" + key_url + '/'
    spider = Spider()
    chapters, introduce, title = spider.get_lists(full_url)
    return render_template('novel/novel_chapters.html', introduce=introduce, chapters=chapters, title=title)


@novel_blueprint.route('/novel/<key_url>/<key_page>')
def novel_page(key_url, key_page):
    full_url = "http://www.biquge5200.com/" + key_url + '/' + key_page
    try:
        spider = Spider()
        page, title = spider.get_page(full_url)
    except ValueError:
        return redirect(url_for('novel.novel_chapters', key_url=key_url))
    else:
        key = [key_url, key_page]
        return render_template('novel/novel_page.html', page=page, title=title, key=key)


@novel_blueprint.route('/api/add_novel', methods=['POST'])
def add_novel():
    book_link = request.values.get('link')
    book_name = request.values.get('book_name')
    if book_name and book_link:
        # 这里有个爬取 作者 更新日期 创建日期为 自己加入书架的日期 本书状态 最新一章
        image, author, modified_date, status = Spider.get_message(book_link)
        case = Book()
        case.name = book_name
        case.link = book_link
        case.author = author
        case.modified_date = modified_date
        # case.latest_chapter = latest_chapter
        try:
            db.session.add(case)
            db.session.commit()
        except:
            return "无法再次添加书籍"
        return '添加成功', 200
    else:
        return 'fail', 402
        # 请求格式正确, 但由于语法错误, 无法响应


@novel_blueprint.route('/novel/case')
def novel_cases():
    cases = Book.query.order_by(Book.publish_date.desc())
    return render_template('novel/novel_cases.html', cases=cases)


@novel_blueprint.route('/api/delete_novel', methods=['POST'])
def delete_novel():
    name = request.values.get('book_name')
    book = Book.query.filter_by(name=name).first()
    try:
        db.session.delete(book)
        db.session.commit()
    except sqlalchemy.orm.exc.UnmappedInstanceError:
        return "移除失败"
    return redirect(url_for('novel.novel_cases'))
