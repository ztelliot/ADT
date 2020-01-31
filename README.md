# ADT
Auto Dev Tool

## 部署

   ### Docker
    需预先安装好Docker和docker-compose
    git clone后在目录下执行 docker-compose -f adt.yml up -d
    
   ### 非Docker
    安装 python3,python3-pip
    CentOS下还需安装 python3-devel,gcc
    git clone后在目录下执行 pip3 install -r requirements.txt
    然后就可以 python3 main.py 运行

## 基本信息
    本项目是利用subprocess执行指令实现的
    config.json为配置文件，可以设置监听ip、端口、面板用户名、密码和API地址(请在部署前修改)，并且存放了项目数
    project.json存放项目信息
    logs存放日志文件，将被映射至容器内部
    
## 前端部署
    已映射80端口，但需自行选择服务端安装
    例如:
        安装nginx用于前端部署
            构建环境：apt install -y nginx
            构建脚本：service nginx start && cd /var/www/html && git clone https://github.com/ziahamza/webui-aria2.git
            进行构建
            然后就可以通过 http://ip:web_port/webui-aria2/docs 访问
    
## api请求(自动构建)
    外部API请求地址为 http://ip:port/api_key/api
        例如:
            http://192.168.1.100/demo_api_key/api
    api调用方式为GET，参数包括build,test和release
        例如:
            构建项目1 http://192.168.1.100/demo_api_key/api?build=1
            构建并测试项目2 http://192.168.1.100/demo_api_key/api?build=2&test=2
            构建项目1测试项目2发布项目3 http://192.168.1.100/demo_api_key/api?build=1&test=2&release=3
    默认返回success
    如果执行失败会返回错误信息和执行日志
