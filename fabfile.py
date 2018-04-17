from fabric.api import local, run, env, put, abort, run, cd, sudo, roles, execute
from fabric.contrib.console import confirm
import os, time, datetime
from fabric.network import ssh


# remote ssh credentials
#env.hosts = ['shopping-tool-stage.allume.co']
env.path = '/home/ec2-user'
env.user = 'ec2-user'
#ssh.util.log_to_file("paramiko.log", 10)


env.current_path = "%s/current" % (env.path)
env.releases_path = "%s/releases" % (env.path)
env.shared_path = "%s/shared" % (env.path)
env.git_clone = "git@github.com:allume/clio.git"
env.git_clone_branch = "develop"
env.current_release = "%s/%s" % (env.releases_path, datetime.datetime.now().strftime("%Y-%m-%d-%H-%M"))
env.max_releases = 10
env.environment = 'qa'


#env.virtualhost_path = "/"

# tasks

# specify path to files being deployed
env.archive_source = '.'

# archive name, arbitrary, and only for transport
env.archive_name = 'release'

# specify path to deploy root dir - you need to create this
env.deploy_project_root = '/var/www/clio/'

# specify name of dir that will hold all deployed code
env.deploy_release_dir = 'releases'

# symlink name. Full path to deployed code is env.deploy_project_root + this
env.deploy_current_dir = 'current'


#Define Hosts
def qa(docker_tag=''):
  env.user = 'ec2-user'
  env.environment = 'qa'

  env.roledefs = {
      'web': ['ec2-13-56-37-140.us-west-1.compute.amazonaws.com'],
      'worker': ['ec2-52-8-79-129.us-west-1.compute.amazonaws.com'],
  }

  if docker_tag == '':
    env.docker_tag = 'develop'
  else:
    env.docker_tag = docker_tag

def prod(docker_tag=''):
  env.user = 'ec2-user'
  env.environment = 'prod'
  env.docker_tag = 'master'

  env.gateway = 'ec2-52-53-136-112.us-west-1.compute.amazonaws.com'

  env.roledefs = {
      'web': ['ec2-54-177-92-201.us-west-1.compute.amazonaws.com'],
      'worker': ['ec2-54-176-139-176.us-west-1.compute.amazonaws.com'],
      #'web': ['127.0.0.1:8022'],
      #'worker': ['127.0.0.1:8023'],
  }


@roles(['web', 'worker'])
def df():
  run('df -h')

@roles(['web', 'worker'])
def free():
  run('free -m')

@roles(['web', 'worker'])
def docker_ps():
  run('docker ps')

@roles(['web', 'worker'])
def docker_images():
  run('docker images')

@roles('web')
def restart_nginx():
    run('docker restart $(docker ps -a -q --filter name=shopping_tool_nginx)')

@roles('web')
def restart_web():
    run('docker restart $(docker ps -a -q --filter name=shopping_tool_web)')

@roles('web')
def restart():
    print('Restarting UWSGI/Web')
    restart_web()
    print('Restarting Nginx')
    restart_nginx()

@roles(['web', 'worker'])
def clean_up_docker():
    env.warn_only = True#Allows process to proceed if there is no current container
    run('docker rm -v $(docker ps -a -q -f status=exited)')
    image_clean_result = run('docker rmi $(docker images -f "dangling=true" -q)')
    env.warn_only = False

@roles('web')
def deploy_nginx():
    #Restart Nginx
    run("docker pull raybeam/nginx:latest")
    env.warn_only = True#Allows process to proceed if there is no current container
    run('docker rm $(docker stop $(docker ps -a -q --filter name=nginx))')
    env.warn_only = False
    run("docker run --restart=on-failure -d -v /etc/nginx:/etc/nginx -v /etc/pki/nginx:/etc/pki/nginx -p 80:80 -p 443:443 --link %s_flower:%s_flower --link %s_shopping_tool_web:%s_shopping_tool_web --volumes-from %s_shopping_tool_web --name %s_shopping_tool_nginx raybeam/nginx" % (env.environment, env.environment, env.environment, env.environment, env.environment, env.environment))

@roles('web')
def deploy_flower():
    #Restart Nginx
    run("docker pull elsdoerfer/docker-celery-flower")
    env.warn_only = True#Allows process to proceed if there is no current container
    run('docker rm $(docker stop $(docker ps -a -q --filter name=flower))')
    env.warn_only = False
    run("docker run -d -p 5555:5555 --name=%s_flower elsdoerfer/docker-celery-flower flower --broker=$(<catalogue_service/flower_broker.cfg) --url_prefix=flower" % (env.environment))


@roles('web')
def deploy_web_container():
    #Restart UWSGI - Web Server
    run("docker pull allumestyle/catalogue-service:%s" % (env.docker_tag))  # Add Tag
    
    env.warn_only = True #Allows process to proceed if there is no current container
    run('docker rm $(docker stop $(docker ps -a -q --filter name=web))')
    env.warn_only = False

    run("docker run --restart=on-failure -d -v $(pwd)/catalogue_service/settings_local.py:/srv/catalogue_service/catalogue_service/settings_local.py -v ~/static:/srv/catalogue_service/static -p 8000:8000 --name %s_shopping_tool_web --entrypoint=\"/docker-entrypoint-web.sh\" allumestyle/catalogue-service:%s" % (env.environment, env.docker_tag))

@roles('worker')
def deploy_celery_container():

    run("docker pull allumestyle/catalogue-service:%s" % (env.docker_tag))  # Add Tag

    #Restart Celery
    env.warn_only = True#Allows process to proceed if there is no current container
    run('docker rm $(docker stop $(docker ps -a -q --filter name=celery))')
    env.warn_only = False

    run("docker run --restart=on-failure -d -v $(pwd)/catalogue_service/settings_local.py:/srv/catalogue_service/catalogue_service/settings_local.py -v /var/run/docker.sock:/var/run/docker.sock --name=%s_shopping_tool_celery --entrypoint=\"/docker-entrypoint-celery.sh\" allumestyle/catalogue-service:%s >> ~/shopping_tool_celery.log 2>&1" % (env.environment, env.docker_tag))

    #Restart Celery Beat
    env.warn_only = True#Allows process to proceed if there is no current container
    run('docker rm $(docker stop $(docker ps -a -q --filter name=celery_beat))')
    env.warn_only = False

    run("docker run --restart=on-failure -d -v $(pwd)/catalogue_service/settings_local.py:/srv/catalogue_service/catalogue_service/settings_local.py --name=%s_shopping_tool_celery_beat --entrypoint=\"/docker-entrypoint-celery-beat.sh\" allumestyle/catalogue-service:%s >> ~/shopping_tool_celery_beat.log 2>&1" % (env.environment, env.docker_tag))
    

@roles(['web', 'worker'])
def deploy():
    execute(deploy_web_container)
    execute(deploy_celery_container)
    execute(deploy_nginx)
    execute(clean_up_docker)
    #deploy_udfs()
    print('deploy complete!')
