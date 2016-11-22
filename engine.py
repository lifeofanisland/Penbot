#!/usr/bin/python
import web
import MySQLdb
import sqlite3
import urllib2
render = web.template.render('templates/')
urls = (
    '/', 'index',
    '/login', 'login',
    '/auth', 'auth',
    '/register', 'register',
    '/about', 'about',
    '/user/(.*)', 'user',
    '/masthead', 'masthead',
    '/faq', 'faq',
    '/how', 'how',
    '/logout', 'logout',
    '/account', 'account',
    '/(.*)', 'nopage'
)
#define variables
DBN = 'sqlite'
DB_TABLE = 'users'
DB_USER = 'test'
DB_PASS = '123456'
DB_HOST = '127.0.0.1'
DB_PORT = 80

#app title
apptitle = 'Penbot'

#app description
appdescription = [apptitle,'An automated cloud based pension software that runs itself']

#login info
loginfo = ''

#db connection
conn = sqlite3.connect(apptitle+'.db',check_same_thread=False)
cur = conn.cursor()
#db = web.database(dbn=DBN, db=apptitle+'.db')

#create user info table
cur.execute('''CREATE TABLE IF NOT EXISTS users
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
             fullname TEXT,
             email TEXT,
             phone TEXT,
             password TEXT,
             chkuser TEXT);
            ''')
#create activities table
cur.execute('''CREATE TABLE IF NOT EXISTS activities
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
             uid INTEGER,
             typ TEXT,
             descr TEXT,
             tym TEXT);
            ''')

#app calling
app = web.application(urls, globals())

#calling sessions
if web.config.get('_session') is None:
    session = web.session.Session(app,web.session.DiskStore('./sessions'),
    initializer=  {'id':0,'uname': 'null','auth':0,'email':'null','phone':'null','fullname':'null','udata':'null'})
    web.config._session = session
else: 
    session = web.config._session

#get header   
def get_header(name):
        global session
        checkuser = session.udata
        return render.masthead(name,checkuser,appdescription)
    


#insert new user
def new_user(fullname,email,phone,password):
    global cur
    tuser = (email,)
    verifyuser = cur.execute("update users set chkuser='' where email=?", (email,)).rowcount
    if(verifyuser is 0):
         if(cur.execute("insert into users(fullname,email,phone,password,chkuser) values (?,?,?,?,?)", (fullname,email,phone,password,'',))):
            return 1
         else:
            return 0
        
    else:
        loginfo = 'An account with this email address, '+email+' already exists'
        return render.incorrect('Oops...',loginfo)
        
#new activity
def new_activity(_id,typ,descr):
    global cur
    tuser = (_id,)
    verifyuser = cur.execute("update users set chkuser='' where id=?", (_id,)).rowcount
    print verifyuser
    if(verifyuser is 1):
         if(cur.execute("insert into activities(uid,typ,descr) values (?,?,?)", (_id,typ,descr,))):
            return 1
         else:
            return 0
        
    else:
        loginfo = 'An error occured'
        return render.incorrect('Oops...',loginfo)

#get activities
def get_activities():
    global session
    global cur
    _id = session.id
    _dataout = ''
    _data = cur.execute("SELECT * from activities where uid=?", (_id,))
    for row in _data:
        print row[3]
        _dataout += '<div class="activities">'+row[3]+'</div>'
        
    return _dataout

class index:
    def GET(self):
        name = 'Home'
        getheader = get_header(name)
        return render.index(name,appdescription,getheader)

class login:
    def GET(self):
        name = 'Login'
        getheader = get_header(name)
        return render.login(name,appdescription,getheader)

class logout:
    def GET(self):
        name = 'Logout'
        getheader = get_header(name)
        session.kill()
        return web.seeother('/',get_header(''))
    
class account:
    def POST(self):
        global session
        i = web.input()
        fullname = i.fullname
        email = i.email
        phone = i.phone
        password = i.password
        adduser = new_user(fullname,email,phone,password)
        if(adduser is not 0):
            loginfo = 'Account was successfully created.'
            return render.successful('Welcome to '+apptitle,loginfo,'login')
        else:
            loginfo = 'An error occured, please try again in a few minutes.'
            return render.incorrect('Oops...',loginfo)

class auth:
    def POST(self):
        global session
        global conn
        global cur
        i = web.input()
        user = i.user
        passwd = i.passw
        tuser = (user,passwd)
        auth_pass = 0
        verifyuser = cur.execute("update users set chkuser='' where email=? and password=?", tuser).rowcount
        if(verifyuser is 1):
             authuser = cur.execute("SELECT id,fullname,email,phone,password from users where email=? and password=?", tuser)      
             for row in authuser:
                auth_pass = 1
                session.id = row[0]
                session.name = row[1]
                session.email =  row[2]
                session.phone =  row[3]
        
             excluder = 'ok'
             makeudata = str(session.id)+','+str(session.name+',')+str(session.email)+','+str(session.phone)
             session.udata = [session.id,session.name,session.email,session.phone]
        if(auth_pass is 0):
            loginfo = 'Incorrect login credentials'
            return render.incorrect('Unable to sign in',loginfo)
        else:
            new_activity(str(session.id),'login','You logged in to your account')
            return web.seeother('/user/'+session.name,get_header(''))

class register:
    def GET(self):
        name = 'Register'
        getheader = get_header(name)
        return render.register(name,appdescription,getheader)

class about:
    def GET(self):
        name = 'About'
        getheader = get_header(name)
        return render.about(name,appdescription,getheader)

class faq:
    def GET(self):
        name = 'FAQ'
        getheader = get_header(name)
        return render.faq(name,appdescription,getheader)

class how:
    def GET(self):
        name = 'How '+apptitle+' works'
        getheader = get_header(name)
        return render.how(name,appdescription,getheader)

class user:
    def GET(self,name):
        if(len(name) > 1):
           excluder = 'ok';
           getheader = get_header(name)
           checkuser = session.udata
           return render.user(name,checkuser,excluder,getheader,get_activities())
        else:
           return render.notfound(name) 

#not found        
def notfound():
	       return web.notfound(render.notfound(render))
          

#internal error
def internalerror():
	       return web.internalerror(render.internalerror(render))
               
app.notfound = notfound
app.internalerror = internalerror

class nopage:
    def GET(self,name):
        return render.notfound(name)
    
if __name__ == "__main__":
    app.run()
