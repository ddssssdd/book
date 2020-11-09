from requests_html import HTMLSession;
import pymysql;
session = HTMLSession();
db = pymysql.connect('127.0.0.1','sfu','P@ss!2#4%6','test_db',3307);
q = db.cursor();
#indexPage = session.get('https://www.biquge.com.cn/book/44875/');
def updateBook(bookId,urlBook):
    indexPage = session.get(urlBook);
    urls = indexPage.html.find("#list a");
    i = 1;
    for item in urls:
        #print(item.text);
        url = item.absolute_links.pop();
        print(url);
        q.execute('select count(0) from book_content where bookId=%d and url="%s"' % (bookId,url));
        urlExists = q.fetchone()[0];
        if urlExists==0:
            page = session.get(url);
            content = page.html.find("#content",first=True).text;
            #print(content);
            q.execute("insert into book_content(bookId,`index`,url,title,content,last_update) values(%d,%d,'%s','%s','%s',current_timestamp())" % (bookId,i,url,item.text,content));
            db.commit();
            #print(url);
        i = i+1;
    
    