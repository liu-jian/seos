from flask import Flask, render_template, session, redirect, url_for, flash
from flask.ext.script import Manager
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from flask.ext.wtf import Form
from wtforms import TextAreaField,StringField,SubmitField,SelectField,PasswordField
from wtforms.validators import Required,DataRequired
import os,commands,subprocess,time,threading
from webpath import webpath
from userdata import userdata

app = Flask(__name__)
app.config['SECRET_KEY'] = 'who is your boss'

manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)

def gettime():
        ISOTIMEFORMAT='%Y-%m-%d %X'
        ttime = time.strftime( ISOTIMEFORMAT,time.localtime(time.time()))
        return ttime

def make_list(listin,symbol):
        tem = listin.replace(symbol,'')
        tem1 = tem.splitlines()
        return tem1

def inputF(con):
        f = open('seos.log','a')
        updatetime = gettime()
        uptime = str(updatetime) + '\n'
        f.write(uptime)
        conx = con + '\n'
        f.write(conx)
        f.close()

def getweb():
    p = subprocess.Popen('salt-run manage.up | grep web',shell=True,stdout=subprocess.PIPE)
    tem0 = p.stdout.read()
    tem2 = make_list(tem0,'- ')
    return tem2

def rmcache_Newwanbu(webname):
        wbapp = 'Active template Activity Admin Api Article Blog Circle Club Group Groups HealthKnowledge Help Home Lease Manage Message Meter NewVote OutdoorAct Payment PhoneApi Prefecture Public Setting Space Subject Task User Vote Wap Weibo'
        tem2 = getweb()
        basicpath = webpath.get(webname)
        res = subprocess.Popen('salt \'%s\' cmd.run \'sh %scleanwanbucache.sh %s\'' % (webname, basicpath, wbapp),shell=True,stdout=subprocess.PIPE)


def rmomscache_new(webname):
    path = 'oms/Runtime/*'
    basicpath = webpath.get(webname)
    tpath = '%s%s' % (basicpath, path)
    res = subprocess.Popen('salt \'%s\' cmd.run \'rm -rf %s\'' % (webname, tpath),shell=True,stdout=subprocess.PIPE)

def getthreads(targets):
        allweb = getweb()
        threads = []
        for webname in allweb:
                t = threading.Thread(target=targets, args=(webname,))
                threads.append(t)
        return threads

def update_web(path):
        f = open('resault.txt','a')
        tem2 = getweb()
        for webname in tem2:
                basicpath = webpath.get(webname)
                tpath = '%s%s' % (basicpath, path)
                res = subprocess.Popen('salt \'%s\' cmd.run \'svn update %s\'' % (webname, tpath),shell=True,stdout=subprocess.PIPE)
                res_in = res.stdout.read()
                f.write(str(res_in))
                res_list = make_list(res_in,'    ')
        f.close()
        resault = open('resault.txt').read()
        f.close()
        os.remove('resault.txt')
        return resault

class NameForm(Form):
    uppath = SelectField('Path', choices=[('do','do'),('oms','oms'),('oms/Apps/Admin','oms/Apps/Admin'),('NewWanbu','NewWanbu'),('NewWanbu/App/Active','NewWanbu/App/Active'),('NewWanbu/App/Admin','NewWanbu/App/Admin'),('NewWanbu/App/Subject','NewWanbu/App/Subject'),('NewWanbu/App/Groups','NewWanbu/App/Groups'),('NewWanbu/App/Api','NewWanbu/App/Api'),('NewWanbu/App/Wap','NewWanbu/App/Wap')])
    username = SelectField('User', choices=[('wangjy','wangjy'),('fuyn','fuyn'),('gongzw','gongzw'),('liujian','liujian'),('heyu','heyu')])
    upkey = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Update')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route('/', methods=['GET', 'POST'])
def index():
    name = None
    uppath = None
    username = None
    upkey = None
    passwd = None
    rmcache = 'Does it need to delete the cache'
    form = NameForm()
    if form.validate_on_submit():
        uppath = form.uppath.data
        upkey = form.upkey.data
        username = form.username.data
        passwd = userdata.get(username)
        if upkey is None or upkey != passwd:
                flash('Your key is wrong!')
                session['name'] = 'Please input right key.'
                session['rmcache'] = 'Does it need to delete the cache'
                return redirect(url_for('index'))
        else:
                utime = gettime()
                print '%s Start update WEB' % utime
                resaul = update_web(uppath)
                resault = resaul.replace('\n','<br>')
                session['name'] = resault
                if uppath.startswith('NewWanbu'):
                        NewWanbutime = gettime()
                        print '%s NewWanbu is updated,start remove cache.' % NewWanbutime
                        threads = getthreads(rmcache_Newwanbu)
                        for t in threads:
                                t.setDaemon(True)
                                t.start()
                        t.join()
                        endtime = gettime()
                        print '%s NewWanbu upgrade over!' % endtime
                        session['rmcache'] = 'Delete NewWanbu Cache.'
                        uplog = 'Operator:' + username + '\n' + 'Update Path:' + uppath + '\n' + resaul
                        inputF(uplog)
                        print 'NewWanbu: %s' % resaul
                        return redirect(url_for('index'))
                elif uppath.startswith('oms'):
                        omstime = gettime()
                        print '%s oms id updated,start remove cache.' % omstime
                        threads = getthreads(rmomscache_new)
                        for t in threads:
                                t.setDaemon(True)
                                t.start()
                        t.join()
                        endtime = gettime()
                        print '%s oms upgrade over!' % endtime
                        session['rmcache'] = 'Delete oms Cache.'
                        uplog = 'Operator:' + username + '\n' + 'Update Path:' + uppath + '\n' + resaul
                        inputF(uplog)
                        print 'oms:%s' % resaul
                        return redirect(url_for('index'))
                else:
                        session['rmcache'] = 'No need delete cache.'
                        uplog = 'Operator:' + username + '\n' + 'Update Path:' + uppath + '\n' + resaul
                        inputF(uplog)
                        print 'other: %s' % resaul
                        return redirect(url_for('index'))
    return render_template('index.html', form=form, name=session.get('name'), uppath=uppath, upkey=upkey, username = username, rmcache=session.get('rmcache'))


if __name__ == '__main__':
    manager.run()
