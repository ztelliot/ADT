"""
Build by Elliot
"""
# -*- coding:utf-8 -*-
from functools import wraps
from flask import Flask, render_template, request, redirect, session
import psutil
import json
import subprocess
import time
from crontab import CronTab


app = Flask(__name__)
app.secret_key = "!@#$%^&*()"
cron = CronTab(user='root')


with open('config.json', 'r') as rf:
    config = rf.read()
config = eval(config)
rf.close()
user = config['usr']
api_key = config['api_key']


def get_num():
    with open('config.json', 'r') as rf:
        config = rf.read()
    config = eval(config)
    rf.close()
    return config['num']


def calculate():
    with open('config.json', 'r') as rf:
        config = rf.read()
    config = eval(config)
    rf.close()
    num = config['num']
    id = 1
    with open('project.json', 'r') as rf:
        project = rf.read()
    project = eval(project)
    rf.close()
    bsuccess = 0
    tsuccess = 0
    while id <= num:
        if project[str(id)]['build_status'] == 1:
            bsuccess += 1
        if project[str(id)]['test_status'] == 1:
            tsuccess += 1
        id += 1
    config['bsuccess'] = bsuccess
    config['tsuccess'] = tsuccess
    with open('config.json', 'w') as cf:
        cf.write(json.dumps(config))
    cf.close()


def dell(id):
    with open('config.json', 'r') as rf:
        config = rf.read()
    config = eval(config)
    rf.close()
    num = config['num']
    with open('project.json', 'r') as rf:
        project = rf.read()
    project = eval(project)
    rf.close()
    if project[id]['cron'] == 1:
        for job in cron:
            if job.comment == id:
                cron.remove(job)
                cron.write()
        project[id]['cron'] = 0
    i = 1
    while int(id) + i <= num:
        project[str(int(id) + i - 1)] = project[str(int(id) + i)]
        i += 1
    num -= 1
    config['num'] = num
    with open('project.json', 'w') as cf:
        cf.write(json.dumps(project))
    cf.close()
    with open('config.json', 'w') as cf:
        cf.write(json.dumps(config))
    cf.close()
    subprocess.getstatusoutput('rm -rf logs/' + id + '*')


def wrapper(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if session.get("user"):
            ret = func(*args, **kwargs)
            return ret
        else:
            return redirect("/login")
    return inner


@app.route('/')
def index():
    if session.get("user"):
        calculate()
        with open('config.json', 'r') as rf:
            config = rf.read()
        config = eval(config)
        rf.close()
        num = config['num']
        meminfo = psutil.virtual_memory().percent
        cpuinfo = psutil.cpu_percent(interval=1, percpu=False)
        pbuild = config['bsuccess']
        ptest = config['tsuccess']
        return render_template('status.html', usr=user, num=num, mem=meminfo, cpu=cpuinfo, build=pbuild, test=ptest, sta='online')
    else:
        return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get("user"):
        return redirect('/')
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        if request.form.get('username') == user and request.form.get("password") == config['key']:
            session['user'] = request.form.get('username')
            return redirect('/')
        else:
            return render_template('login.html', code='err')


@app.route('/logout')
def logout():
    session['user'] = ''
    return redirect('/')


@app.route('/manage')
@wrapper
def control():
    return render_template('manage.html', sign='log', title='欢迎访问管理中心', text='祝宁使用愉快')


@app.route('/manage/info')
@wrapper
def info():
    num = get_num()
    with open('project.json', 'r') as rf:
        project = rf.read()
    project = eval(project)
    rf.close()
    ids = request.args.get("id") or 0
    if int(ids) > num:
        return render_template('manage.html', sign='error', title='错误', text='参数错误')
    if int(ids):
        pre = project[ids]
        name = pre['name']
        b = pre['build']
        bt = pre['latest_build_time']
        t = pre['test']
        tt = pre['latest_test_time']
        r = pre['release']
        rt = pre['latest_release_time']
        status = pre['status']
        if str(status).find('failed') >= 0:
            code = 'danger'
        elif str(status).find('add') >= 0:
            code = 'info'
        else:
            code = 'success'
        return render_template('info.html', name=name, code=code, status=status, build=b, test=t, release=r, bt=bt, tt=tt, rt=rt, id=ids)
    return render_template('info.html')


@app.route('/manage/logs/init')
@wrapper
def log_init():
    num = get_num()
    ids = request.args.get("id") or 0
    if int(ids) > num:
        return render_template('logs.html', sign='error', title='错误', text='参数错误')
    if int(ids):
        try:
            with open('logs/'+ids+'_initialize.log', 'r') as rf:
                log = rf.read()
            rf.close()
            return render_template('logs.html', log=log)
        except:
            return render_template('logs.html', sign='error', title='错误', text='日志打开失败')
    else:
        return render_template('logs.html', sign='error', title='错误', text='参数错误')


@app.route('/manage/logs/build')
@wrapper
def log_build():
    num = get_num()
    ids = request.args.get("id") or 0
    if int(ids) > num:
        return render_template('logs.html', sign='error', title='错误', text='参数错误')
    if int(ids):
        try:
            with open('logs/'+ids+'_build.log', 'r') as rf:
                log = rf.read()
            rf.close()
            return render_template('logs.html', log=log)
        except:
            return render_template('logs.html', sign='error', title='错误', text='日志打开失败')
    else:
        return render_template('logs.html', sign='error', title='错误', text='参数错误')


@app.route('/manage/logs/test')
@wrapper
def log_test():
    num = get_num()
    ids = request.args.get("id") or 0
    if int(ids) > num:
        return render_template('logs.html', sign='error', title='错误', text='参数错误')
    if int(ids):
        try:
            with open('logs/'+ids+'_test.log', 'r') as rf:
                log = rf.read()
            rf.close()
            return render_template('logs.html', log=log)
        except:
            return render_template('logs.html', sign='error', title='错误', text='日志打开失败')
    else:
        return render_template('logs.html', sign='error', title='错误', text='参数错误')


@app.route('/manage/logs/release')
@wrapper
def log_release():
    num = get_num()
    ids = request.args.get("id") or 0
    if int(ids) > num:
        return render_template('logs.html', sign='error', title='错误', text='参数错误')
    if int(ids):
        try:
            with open('logs/'+ids+'_release.log', 'r') as rf:
                log = rf.read()
            rf.close()
            return render_template('logs.html', log=log)
        except:
            return render_template('logs.html', sign='error', title='错误', text='日志打开失败')
    else:
        return render_template('logs.html', sign='error', title='错误', text='参数错误')


@app.route('/manage/add', methods=['GET', 'POST'])
@wrapper
def add():
    if request.method == 'GET':
        return render_template('edit.html', name='name', env='在此键入以配置环境，Eg:apt install -y go', build='./build', test='./test', release='./release')
    elif request.method == 'POST':
        try:
            name = request.form.get('name')
            env = request.form.get('env')
            build_script = request.form.get('build')
            test_script = request.form.get('test')
            release_script = request.form.get('release')
            build_condition = request.form.get('condition')
            if name and build_condition:
                with open('config.json', 'r') as rf:
                    config = rf.read()
                config = eval(config)
                rf.close()
                config['num'] += 1
                num = config['num']
                with open('project.json', 'r') as rf:
                    project = rf.read()
                project = eval(project)
                rf.close()
                project[num] = {
                    "name": name,
                    "env": env,
                    "build_script": build_script,
                    "test_script": test_script,
                    "release_script": release_script,
                    "initialized": 0,
                    "build": 0,
                    "latest_build_time": "",
                    "test": 0,
                    "latest_test_time": "",
                    "release": 0,
                    "latest_release_time": "",
                    "status": "added",
                    "build_status": 0,
                    "test_status": 0,
                    "release_status": 0,
                    "condition": build_condition,
                    "cron": 0
                }
                with open('project.json', 'w') as cf:
                    cf.write(json.dumps(project))
                cf.close()
                with open('config.json', 'w') as cf:
                    cf.write(json.dumps(config))
                cf.close()
                return render_template('manage.html', sign='success', title='项目已添加', text='请继续操作')
            else:
                return render_template('edit.html', sign='error', title='错误', text='至少留个名字啊', name=name, env=env, build=build_script, test=test_script, release=release_script)
        except:
            return render_template('edit.html', sign='error', title='错误', text='请输入正确的信息')


@app.route('/manage/delete')
@wrapper
def delete():
    num = get_num()
    ids = request.args.get("id") or 0
    if int(ids) > num:
        return render_template('manage.html', sign='error', title='错误', text='参数错误')
    if int(ids):
        dell(ids)
        return render_template('manage.html', sign='success', title='成功', text='已删除')


@app.route('/manage/edit', methods=['GET', 'POST'])
@wrapper
def edit():
    num = get_num()
    with open('project.json', 'r') as rf:
        project = rf.read()
    project = eval(project)
    rf.close()
    ids = request.args.get("id") or 0
    if int(ids) > num:
        return render_template('edit.html', sign='error', title='错误', text='参数错误')
    if int(ids):
        pre = project[ids]
        if request.method == 'GET':
            return render_template('edit.html', name=pre['name'], env=pre['env'], build=pre['build_script'], test=pre['test_script'], release=pre['release_script'])
        elif request.method == 'POST':
            try:
                name = request.form.get('name')
                env = request.form.get('env')
                build_script = request.form.get('build')
                test_script = request.form.get('test')
                release_script = request.form.get('release')
                build_condition = request.form.get('condition')
                if name and build_condition:
                    project[ids]['name'] = name
                    if project[ids]['env'] != env:
                        project[ids]['initialized'] = 0
                    project[ids]['env'] = env
                    project[ids]['build_script'] = build_script
                    project[ids]['test_script'] = test_script
                    project[ids]['release_script'] = release_script
                    if project[ids]['condition'] != build_condition:
                        if project[ids]['cron'] == 1 and build_condition != 0:
                            for job in cron:
                                if job.comment == ids:
                                    job.hour.every(int(build_condition) * 24)
                                cron.write()
                        elif project[ids]['cron'] == 1 and build_condition == 0:
                            for job in cron:
                                if job.comment == ids:
                                    cron.remove(job)
                                    cron.write()
                            project[ids]['cron'] = 0
                        elif project[ids]['cron'] == 0 and build_condition != 0:
                            job = cron.new(command=project[ids]['build_script'], comment=ids)
                            job.hour.every(condition * 24)
                            cron.write()
                            project[ids]['cron'] = 1
                        else:
                            pass
                    project[ids]['condition'] = build_condition
                    with open('project.json', 'w') as cf:
                        cf.write(json.dumps(project))
                    cf.close()
                    return render_template('manage.html', sign='success', title='修改成功', text='请继续操作')
                else:
                    return render_template('edit.html', sign='error', title='错误', text='至少留个名字啊', name=name, env=env, build=build_script, test=test_script, release=release_script)
            except:
                return render_template('edit.html', sign='error', title='错误', text='请输入正确的信息')
    else:
        return render_template('edit.html', sign='error', title='错误', text='参数错误')


@app.route('/api')
@wrapper
def api():
    with open('project.json', 'r') as rf:
        project = rf.read()
    project = eval(project)
    rf.close()
    num = get_num()
    idb = request.args.get("build") or 0
    idt = request.args.get("test") or 0
    idr = request.args.get("release") or 0
    idd = request.args.get("delete") or 0
    if int(idb) > num or int(idt) > num or int(idr) > num or int(idd) > num:
        return '参数错误'
    if int(idb):
        if project[idb]['initialized'] == 0:
            (sta, out) = subprocess.getstatusoutput(project[idb]['env'])
            if sta == 0:
                project[idb]['initialized'] = 1
                project[idb]['status'] = 'initialized'
                condition = int(project[idb]['condition'])
                if condition > 0:
                    job = cron.new(command=project[idb]['build_script'], comment=idb)
                    job.hour.every(condition * 24)
                    cron.write()
                    project[idb]['cron'] = 1
                with open('logs/'+idb+'_initialize.log', 'w') as cf:
                    cf.write(out)
                cf.close()
                with open('project.json', 'w') as cf:
                    cf.write(json.dumps(project))
                cf.close()
                with open('project.json', 'r') as rf:
                    project = rf.read()
                project = eval(project)
                rf.close()
            else:
                project[idb]['status'] = 'initialized_failed'
                with open('logs/' + idb + '_initialize.log', 'w') as cf:
                    cf.write(out)
                cf.close()
                with open('project.json', 'w') as cf:
                    cf.write(json.dumps(project))
                cf.close()
                return '初始化环境失败\n'+out
        (sta, out) = subprocess.getstatusoutput(project[idb]['build_script'])
        if sta == 0:
            project[idb]['build'] += 1
            project[idb]['latest_build_time'] = time.asctime()
            project[idb]['status'] = 'build'
            project[idb]['build_status'] = 1
            if project[idb]['cron'] == 0:
                for job in cron:
                    if job.comment == idb:
                        job.enable()
                        cron.write()
                project[idb]['cron'] = 1
            with open('logs/' + idb + '_build.log', 'w') as cf:
                cf.write(out)
            cf.close()
            with open('project.json', 'w') as cf:
                cf.write(json.dumps(project))
            cf.close()
        else:
            project[idb]['latest_build_time'] = time.asctime()
            project[idb]['status'] = 'build_failed'
            project[idb]['build_status'] = 0
            if project[idb]['cron'] == 1:
                for job in cron:
                    if job.comment == idb:
                        job.enable(False)
                        cron.write()
                project[idb]['cron'] = 0
            with open('logs/' + idb + '_build.log', 'w') as cf:
                cf.write(out)
            cf.close()
            with open('project.json', 'w') as cf:
                cf.write(json.dumps(project))
            cf.close()
            return '构建失败\n'+out
    if int(idt):
        if project[idt]['build'] == 0:
            return '尚未构建'
        (sta, out) = subprocess.getstatusoutput(project[idt]['test_script'])
        if sta == 0:
            project[idt]['test'] += 1
            project[idt]['latest_test_time'] = time.asctime()
            project[idt]['status'] = 'tested'
            project[idt]['test_status'] = 1
            with open('logs/' + idt + '_test.log', 'w') as cf:
                cf.write(out)
            cf.close()
            with open('project.json', 'w') as cf:
                cf.write(json.dumps(project))
            cf.close()
        else:
            project[idt]['latest_test_time'] = time.asctime()
            project[idt]['status'] = 'test_failed'
            project[idt]['test_status'] = 0
            with open('logs/' + idt + '_test.log', 'w') as cf:
                cf.write(out)
            cf.close()
            with open('project.json', 'w') as cf:
                cf.write(json.dumps(project))
            cf.close()
            return '测试未通过\n'+out
    if int(idr):
        if project[idr]['build'] == 0:
            return '尚未构建'
        (sta, out) = subprocess.getstatusoutput(project[idr]['release_script'])
        if sta == 0:
            project[idr]['release'] += 1
            project[idr]['latest_release_time'] = time.asctime()
            project[idr]['status'] = 'released'
            project[idr]['release_status'] = 1
            with open('logs/' + idr + '_release.log', 'w') as cf:
                cf.write(out)
            cf.close()
            with open('project.json', 'w') as cf:
                cf.write(json.dumps(project))
            cf.close()
        else:
            project[idr]['latest_release_time'] = time.asctime()
            project[idr]['status'] = 'release_failed'
            project[idr]['release_status'] = 0
            with open('logs/' + idr + '_release.log', 'w') as cf:
                cf.write(out)
            cf.close()
            with open('project.json', 'w') as cf:
                cf.write(json.dumps(project))
            cf.close()
            return '发布不成功\n'+out
    if int(idd):
        try:
            dell(idd)
        except:
            return '删除失败'
    return 'success'


@app.route('/'+api_key+'/api')
def pub_api():
    with open('project.json', 'r') as rf:
        project = rf.read()
    project = eval(project)
    rf.close()
    num = get_num()
    idb = request.args.get("build") or 0
    idt = request.args.get("test") or 0
    idr = request.args.get("release") or 0
    if int(idb) > num or int(idt) > num or int(idr) > num:
        return 'wrong id'
    if int(idb):
        if project[idb]['initialized'] == 0:
            (sta, out) = subprocess.getstatusoutput(project[idb]['env'])
            if sta == 0:
                project[idb]['initialized'] = 1
                project[idb]['status'] = 'initialized'
                condition = int(project[idb]['condition'])
                if condition > 0:
                    job = cron.new(command=project[idb]['build_script'], comment=idb)
                    job.hour.every(condition * 24)
                    cron.write()
                    project[idb]['cron'] = 1
                with open('logs/'+idb+'_initialize.log', 'w') as cf:
                    cf.write(out)
                cf.close()
                with open('project.json', 'w') as cf:
                    cf.write(json.dumps(project))
                cf.close()
                with open('project.json', 'r') as rf:
                    project = rf.read()
                project = eval(project)
                rf.close()
            else:
                project[idb]['status'] = 'initialized_failed'
                with open('logs/' + idb + '_initialize.log', 'w') as cf:
                    cf.write(out)
                cf.close()
                with open('project.json', 'w') as cf:
                    cf.write(json.dumps(project))
                cf.close()
                return 'initialized failed\n'+out
        (sta, out) = subprocess.getstatusoutput(project[idb]['build_script'])
        if sta == 0:
            project[idb]['build'] += 1
            project[idb]['latest_build_time'] = time.asctime()
            project[idb]['status'] = 'build'
            project[idb]['build_status'] = 1
            if project[idb]['cron'] == 0:
                for job in cron:
                    if job.comment == idb:
                        job.enable()
                        cron.write()
                project[idb]['cron'] = 1
            with open('logs/' + idb + '_build.log', 'w') as cf:
                cf.write(out)
            cf.close()
            with open('project.json', 'w') as cf:
                cf.write(json.dumps(project))
            cf.close()
        else:
            project[idb]['latest_build_time'] = time.asctime()
            project[idb]['status'] = 'build_failed'
            project[idb]['build_status'] = 0
            if project[idb]['cron'] == 1:
                for job in cron:
                    if job.comment == idb:
                        job.enable(False)
                        cron.write()
                cron.write()
                project[idb]['cron'] = 0
            with open('logs/' + idb + '_build.log', 'w') as cf:
                cf.write(out)
            cf.close()
            with open('project.json', 'w') as cf:
                cf.write(json.dumps(project))
            cf.close()
            return 'build failed\n'+out
    if int(idt):
        if project[idt]['build'] == 0:
            return 'please build first'
        (sta, out) = subprocess.getstatusoutput(project[idt]['test_script'])
        if sta == 0:
            project[idt]['test'] += 1
            project[idt]['latest_test_time'] = time.asctime()
            project[idt]['status'] = 'tested'
            project[idt]['test_status'] = 1
            with open('logs/' + idt + '_test.log', 'w') as cf:
                cf.write(out)
            cf.close()
            with open('project.json', 'w') as cf:
                cf.write(json.dumps(project))
            cf.close()
        else:
            project[idt]['latest_test_time'] = time.asctime()
            project[idt]['status'] = 'test_failed'
            project[idt]['test_status'] = 0
            with open('logs/' + idt + '_test.log', 'w') as cf:
                cf.write(out)
            cf.close()
            with open('project.json', 'w') as cf:
                cf.write(json.dumps(project))
            cf.close()
            return 'test failed\n'+out
    if int(idr):
        if project[idr]['build'] == 0:
            return 'please build first'
        (sta, out) = subprocess.getstatusoutput(project[idr]['release_script'])
        if sta == 0:
            project[idr]['release'] += 1
            project[idr]['latest_release_time'] = time.asctime()
            project[idr]['status'] = 'released'
            project[idr]['release_status'] = 1
            with open('logs/' + idr + '_release.log', 'w') as cf:
                cf.write(out)
            cf.close()
            with open('project.json', 'w') as cf:
                cf.write(json.dumps(project))
            cf.close()
        else:
            project[idr]['latest_release_time'] = time.asctime()
            project[idr]['status'] = 'release_failed'
            project[idr]['release_status'] = 0
            with open('logs/' + idr + '_release.log', 'w') as cf:
                cf.write(out)
            cf.close()
            with open('project.json', 'w') as cf:
                cf.write(json.dumps(project))
            cf.close()
            return 'release failed\n'+out
    return 'success'


@app.route('/info')
@wrapper
def html():
    num = get_num()
    with open('project.json', 'r') as rf:
        project = rf.read()
    project = eval(project)
    rf.close()
    i = 1
    data = '<tr><td style="width: 10%" class="td_top"></td><td style="width: 30%" class="td_top">项目名</td><td style="width: 30%" class="td_top">状态</td><td style="width: 30%" class="td_top">操作</td></tr>'
    while i <= num:
        status = project[str(i)]['status']
        if str(status).find('failed') >= 0:
            style = 'danger'
        else:
            style = 'success'
        data += '<tr><td>' + str(i) + '</td><td>' + project[str(i)][
            'name'] + '</td><td class=\'text-' + style + '\'>' + status + '</td><td><button class=\'btn btn-info\' onclick="location.href=\'/manage/info?id=' + str(
            i) + '\'">查看</button><button class=\'btn btn-warning\' onclick="location.href=\'/manage/edit?id=' + str(
            i) + '\'">编辑</button><button class=\'btn btn-danger\' onclick="location.href=\'/manage/delete?id=' + str(
            i) + '\'">删除</button></td></tr>'
        i += 1
    return data


if __name__ == '__name__':
    app.run()
