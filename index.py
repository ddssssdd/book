from flask import Flask;
from flask import render_template,request,redirect,url_for;
from requests_html import HTMLSession;
import pymysql;

app = Flask(__name__);



@app.route("/")
def index():
    return "hello";

@app.route("/book/<bookId>/<urlId>")
def book(bookId,urlId):
    db = pymysql.connect("127.0.0.1","sfu","P@ss!2#4%6","test_db",3307);
    cursor = db.cursor();
    cursor.execute("select title,content,`index` from book_content where bookId=%s and `index`=%s" % (bookId,urlId));
    book = cursor.fetchone()
    content = book[1];
    content = content.replace('\n','<br/>');
    #print(content);
    title = book[0];
    return render_template("index.html",content=content,title=title,urlId=int(urlId),bookId=bookId);

@app.route("/list/<bookId>")
def list(bookId):
    db = pymysql.connect("127.0.0.1","sfu","P@ss!2#4%6","test_db",3307);
    cursor = db.cursor();
    cursor.execute("select title,content,`index` from book_content where bookId=%s" % (bookId));
    urls = cursor.fetchall();
    c2 =db.cursor();
    c2.execute("select title from book_list where bookId=%s" % (bookId));
    bookName = c2.fetchone()[0];
    return render_template("list.html",urls=urls,bookId=bookId,bookName=bookName);
@app.route("/home/")
def home():
    db = pymysql.connect("127.0.0.1","sfu","P@ss!2#4%6","test_db",3307);
    cursor = db.cursor();
    cursor.execute("select bookId,url,title,author from book_list");
    books = cursor.fetchall();
    return render_template("home.html",books=books);
@app.route("/bookRemove/<bookId>")
def bookRemove(bookId):
    db = pymysql.connect("127.0.0.1","sfu","P@ss!2#4%6","test_db",3307);
    cursor = db.cursor();
    cursor.execute("delete from book_list where bookId=%s" % (bookId));
    db.commit();
    return redirect(url_for("home"));
@app.route("/bookAdd/",methods=["POST"])
def bookAdd():
    bookId = request.form.get("bookId");
    #print(bookId);
    url = request.form.get("url");
    title = request.form.get("title");
    author = request.form.get("author");
    db = pymysql.connect("127.0.0.1","sfu","P@ss!2#4%6","test_db",3307);
    cursor = db.cursor();
    cursor.execute("insert into book_list(bookId,url,title,author) values(%s,'%s','%s','%s')" % (bookId,url,title,author));
    db.commit();
    return redirect(url_for("home"));
@app.route("/updateBook/<bookId>")
def updateBook(bookId):
    db = pymysql.connect("127.0.0.1","sfu","P@ss!2#4%6","test_db",3307);
    c2 = db.cursor();
    c2.execute("select title,url,last_update from book_list where bookId=%s" % (bookId));
    rs = c2.fetchone();
    url = rs[1];
    updateBookFromInternetv2(bookId,url);
    return list(bookId);
def updateBookFromInternetv2(bookId,urlBook):
    session = HTMLSession();
    indexPage = session.get(urlBook);
    urls = indexPage.html.find("#list a");
    i = 1;
    db = pymysql.connect("127.0.0.1","sfu","P@ss!2#4%6","test_db",3307);
    q = db.cursor();
    beginUpdate = 0;
    lastUpdate = 'unknown';
    q.execute('select `index`,url from book_content where bookId=%s order by `index` desc limit 1' % (bookId));
    row = q.fetchone();
    if row:
        lastUpdate=row[1];
        print('found');
    else:
        beginUpdate = 1;
        print('not found');
    
    for item in urls:
        #print(item.text);
        url = item.absolute_links.pop();
        
        urlExists = beginUpdate;
        if urlExists>0:
            page = session.get(url);
            content = page.html.find("#content",first=True).text;
            #print(content);
            #q.execute("insert into book_content(bookId,`index`,url,title,content,last_update) values(%s,%d,'%s','%s','%s',current_timestamp())" % (bookId,i,url,item.text,content));
            c = db.cursor();
            try:
                c.execute("insert into book_content(bookId,`index`,url,title,content,last_update) values({0},{1},'{2}','{3}','{4}',current_timestamp())".format(bookId,beginUpdate,url,item.text,content));
                db.commit();
            except:
                db.rollback();
            print(url);
            beginUpdate = beginUpdate +1; 
        if url==lastUpdate:
            beginUpdate=row[0]+1;
            print(row[0]);
           
def updateBookFromInternet(bookId,urlBook):
    session = HTMLSession();
    indexPage = session.get(urlBook);
    urls = indexPage.html.find("#list a");
    i = 1;
    db = pymysql.connect("127.0.0.1","sfu","P@ss!2#4%6","test_db",3307);
    q = db.cursor();
    for item in urls:
        #print(item.text);
        url = item.absolute_links.pop();
        
        q.execute('select count(0) from book_content where bookId=%s and url="%s"' % (bookId,url));
        urlExists = q.fetchone()[0];
        if urlExists==0:
            page = session.get(url);
            content = page.html.find("#content",first=True).text;
            #print(content);
            #q.execute("insert into book_content(bookId,`index`,url,title,content,last_update) values(%s,%d,'%s','%s','%s',current_timestamp())" % (bookId,i,url,item.text,content));
            c = db.cursor();
            try:
                c.execute("insert into book_content(bookId,`index`,url,title,content,last_update) values({0},{1},'{2}','{3}','{4}',current_timestamp())".format(bookId,i,url,item.text,content));
                db.commit();
            except:
                db.rollback();
            print(url);
        i = i+1;    