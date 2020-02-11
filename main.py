from wsgiref.simple_server import make_server
from flaskapp import app as application
import subprocess
if __name__ == "__main__":
    sta = subprocess.getstatus('env >> /etc/default/locale && /etc/init.d/cron start && nginx start')
    if sta == 0:
        print('Env Started!')
    with open('config.json', 'r') as rf:
        config = rf.read()
    rf.close()
    config = eval(config)
    port = config['port']
    ip = str(config['ip'])
    httpd = make_server(ip, port, application)
    print('Server is running on '+ip+':'+str(port))
    httpd.serve_forever()
