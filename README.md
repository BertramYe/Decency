# 在build镜像之前，如果没有建立好数据库，或者需要手动收集静态信息的，可以执行以下命令
# 1) 创建SQL语句
python manage.py makemigrations 【app1_name】【app2_name】 .......
# 2) 进行数据库建表
python manage.py migrate 【app1_name】【app2_name】 .......
# 3) 创建缓存表（如果是使用redis，这一步可以省略）
python manage.py createcachetable 【cache_table_name】
# 例如：
python manage.py createcachetable my_cache_table
# 4) 创建超级用户
python manage.py createsuperuser --username [surper_user_name]
# 5) 在部署完成后需要手动收集一下对应的静态文件，也就是以下命令最好必做
python manage.py collectstatic
# 6) 以下这个命令也是必做，需要将对应的media文件夹下的图片，重新cp到对应的映射路径当中
# /home/Bertram/deceny_data/media/ 为你本地的物理路径信息
cp -r decency/media/* /home/Bertram/deceny_data/media/

# 这个命令有以下可选参数：
usage: manage.py createsuperuser [-h] [--username USERNAME] [--noinput] [--database DATABASE] [--email EMAIL] [--version] [-v {0,1,2,3}]
                                 [--settings SETTINGS] [--pythonpath PYTHONPATH] [--traceback] [--no-color] [--force-color] [--skip-checks]

# 另外如果是完全成熟的MYSQL数据，可能需要做数据迁移，更进一步数据迁移命令，可以参考对应的Msql迁移命令


# add more for the docker-compose

```yml
version: '1.0'

services:
  decency:           # 容器创建完启动时的容器名
    image: decency:v1         # 当同时指定image和build时，docker会将build完的镜像命名为image的名字
    restart: always
    build: 
      context: ../../         # context 上下文路径,也就是项目代码的主路径，可以是文件路径，也可以是到链接到 git 仓库的 url. 当是相对路径时，它被解释为相对于 Compose 文件的位置。
      dockerfile: dockerfile  # 指定构建镜像的名
      # ports:
      #   - 80:8000           # 该子容器项目运行的对外端口80和容器内的端口8000，由于我再dockerfile已经配置，可以省略
    volumes:
      - /decency_data:/decency/media  # 将存储django网站的图片，等信息，挂载到宿主机磁盘
      - /decency_data:/decency/static_collections
    environment:           # 指定当前子容器的环境变量
      - TZ-Asia/Shanghai   # 时区    
      - SECRET_KEY="" 
      - ALLOWED_HOSTS=""   # 允许访问当前网站的主机地址或者域名 
      - CORS_ALLOWED_ORIGINS="http://nginx:8888,http://192.168.0.110:80"   # docker-compose 里面的网路可以使用hostname
      - EMAIL_ADDRESS=""         # 邮件发送服务的邮件地址
      - EMAIL_HOST_PASSWORD=""    # 邮件发送的授权码
      - QQ_APPID=""                      # QQ登录的相关设置
      - QQ_APP_KEY=""  
      - QQ_REDIRECT_URL="http://bertram-world.com/users_managements/login_with_qq"  # 自己申请的当用户登录QQ后在自己网站重定向的地址
      - REDIS_IP_ADDRESS="redis"    # redis的IP地址 docker-compose 里面的网路可以使用hostname
      - REDIS_PORT="6379"      # REDIS的对外端口
      - REDIS_DB="1"           # 使用redis的第几个数据库作为缓存
      - DB_NAME=""          # 以下为数据库登录的信息
      - DB_USERNAME="" 
      - DB_PASSWORD=""  
      # - DB_HOST="172.17.0.2"
      - DB_HOST = "decency-mysql"   # docker-compose 里面的网路可以使用hostname
      - DB_PORT="3306" 
    # networks:
    #   - my_net:
    #       ipv4_address: 172.17.0.2   # 指定当前容器的虚拟IP地址
    command:         # 创建容器时执行的命令
      - cd /decency 
      - python manage.py makemigrations # 如果只是为了迁移django项目，以下建表过程以及超级用户的创建可以不要，由于当前数据库里面已经有了对应信息
      - python manage.py makemigrate
      - python manage.py createsuperuser < superuserinfor.txt  # 这一步是为了创建超级用户superuserinfor.txt里面写好了每一步需要创建的内容
      # - python manage.py createcachetable my_cache_table  由于打算使用redis作为缓存，所以此处缓存表暂时不需要

    entrypoint:        # 每次重启执行的命令
      - cd /decency 
      - python manage.py collectstatic < yes         # 每次启动，或者重启时都重新收集一遍静态文件
      - uwsgi --ini /decency/extra_config/uwsgi/uwsgi.ini

  nginx:
    image: nginx:latest
    restart: always
    ports:
      - 8888:80
    volumes:
      - ../nginx:/etc/nginx        # 将当前物理主机下的文件夹挂载到容器/etc/nginx文件夹下，这样方便我们在本地修改
    # command: command          
    # networks:                   # docker-compose 里面的网络可以使用容器自身的hostname
    #   - my_net:
    #       ipv4_address: 172.17.0.1
  
  # 数据库
  decency_mysql:
    image: mysql:8.0.33
    container_name: decency_mysql
    environment:              # 指定全局变量
      - MYSQL_ROOT_PASSWORD=""  
      - MYSQL_DATABASE="" 
      - MYSQL_USER="" 
      - MYSQL_PASSWORD=""
    ports:
      - 3306:3306

  # 缓存数据库
  redis:
    image: redis:latest
    container_name: redis
    ports:
      - 6379:6379
    # networks:
    #   - networkName
  
  #  environment:  此时由于我们没有配置redis的相关信息，比如登录用户名密码等等，可以不用配置环境变量

```




