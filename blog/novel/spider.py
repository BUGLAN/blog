import re
import os

from blog.novel.download import *


class Novel:
    search_url = "http://www.biquge5200.com/modules/article/search.php"

    def search(self, keyword):
        # biquge 搜索功能
        page = DownLoad.download_page(self.search_url, params={"searchkey": keyword}, timeout=1.5)
        book_message = re.compile('<td class="odd"><a href="(.*?)">(.*?)</a></td>.*?'
                                  '<td class="even"><a href="(.*?)" target="_blank"> (.*?)</a></td>.*?'
                                  '<td class="odd">(.*?)</td>.*?'
                                  '<td class="even">(.*?)</td>.*?'
                                  '<td class="odd" align="center">(.*?)</td>.*?'
                                  '<td class="even" align="center">(.*?)</td>', re.S)
        # 使用正则匹配相应字符串 re.DOTALL / re.S 使'.' 匹配任意字符，包括换行符
        items = book_message.findall(page)
        if items:
            return items
        return None


class BookSpider:
    """
    @:param url: 书籍详情页 如 http://www.biquge5200.com/85_85278/
    """
    chapters = []

    def __init__(self, url):
        self.url = url

    def get_chapters_and_introduce(self):
        # 获取章节目录和介绍
        html = DownLoad.download_page(self.url)
        pattern = re.compile('<div id="intro">.*?<p>(.*?)</p>.*?</div>', re.S)
        introduce = "<p>" + pattern.findall(html)[0] + "</p>"

        pattern = re.compile('<dd><a href="(.*?)">(.*?)</a></dd>')
        chapters = pattern.findall(html)

        title = re.search('<h1>(.*?)</h1>', html).group()

        self.chapters = chapters
        return self.chapters, introduce, title

    def previous_and_next_chapters(self, kurl):
        if not self.chapters:
            BookSpider.get_chapters_and_introduce(self)
        k_index = None
        for url, title in self.chapters:
            if kurl == url:
                k_index = self.chapters.index((url, title))
        if k_index == 0:
            return (os.path.dirname(self.chapters[k_index][0]), '目录'), self.chapters[k_index + 1]
        elif k_index == len(self.chapters) - 1:
            return self.chapters[k_index - 1], (os.path.dirname(self.chapters[k_index][0]), '书籍目录')
        return self.chapters[k_index - 1], self.chapters[k_index + 1]

    @staticmethod
    def get_page(page_url):
        html = DownLoad.download_page(page_url)
        try:
            title = re.search('<h1>(.*?)</h1>', html).group()
            content = re.compile('<div id="content">(.*?)</div>', re.S).findall(html)[0]
            content = re.sub(r'想看好看的小说，请使用微信关注公众号“得牛看书”。', '', content)
        except IndexError as e:
            # content = re.compile('<div id="content">    (.*?)</div>', re.S).findall(html)
            # if content:
            #     print(content)
            #     return content[0]
            return "%s 未获取到内容请联系管理员" % e
        return content, title

    @staticmethod
    def get_message(url):
        html = DownLoad.download_page(url)
        image = re.findall(
            r'<div id="fmimg"><img alt="" src="(.*?)" width="120" height="150"><span class="b"></span></div>',
            html)[0]
        author = re.findall(r'<p style="width:200px">作&nbsp;&nbsp;&nbsp;&nbsp;者：(.*?)</p>', html)[0]
        modified_date = re.findall(r'<p>最后更新：(.*?)</p>', html)[0]
        status = re.findall(r'<meta property="og:novel:status" content="(.*?)"/>', html)[0]
        latest_chapter = re.findall(r"<dd><a href='.*?' >(.*?)</a></dd>", html)[0]
        return image, author, modified_date, status, latest_chapter

# if __name__ == '__main__':
#     book = BookSpider("http://www.biquge5200.com/85_85278")
#     result = book.get_chapters_and_introduce()
#     print(result[0])
#     index = result[0].index(('https://www.biquge5200.com/85_85278/153219401.html', '第232章 核百万'))
#     print(index)
