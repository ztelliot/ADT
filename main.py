from wsgiref.simple_server import make_server
from flaskapp import app as application
if __name__ == "__main__":
    with open('config.json', 'r') as rf:
        config = rf.read()
    rf.close()
    config = eval(config)
    port = config['port']
    ip = str(config['ip'])
    httpd = make_server(ip, port, application)
    print('Server is running on '+ip+':'+str(port))
    httpd.serve_forever()