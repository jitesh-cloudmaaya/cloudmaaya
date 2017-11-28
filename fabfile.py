from fabric.api import local, run, env, put, abort, run, cd, sudo
from fabric.contrib.console import confirm
import os, time, datetime


# remote ssh credentials
env.hosts = ['shopping-tool-stage.allume.co']
env.path = '/home/ec2-user'
env.user = 'ec2-user'


env.current_path = "%s/current" % (env.path)
env.releases_path = "%s/releases" % (env.path)
env.shared_path = "%s/shared" % (env.path)
env.git_clone = "git@github.com:intermix/clio.git"
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
  env.hosts = ['ec2-52-8-79-129.us-west-1.compute.amazonaws.com']

  if docker_tag == '':
    env.docker_tag = 'develop'
  else:
    env.docker_tag = docker_tag


def df():
  run('df -h')

def free():
  run('free -m')

def docker_ps():
  run('docker ps')

def docker_images():
  run('docker images')

def restart_nginx():
    run('docker restart $(docker ps -a -q --filter name=shopping_tool_nginx)')

def restart_web():
    run('docker restart $(docker ps -a -q --filter name=shopping_tool_web)')

def restart():
    print('Restarting UWSGI/Web')
    restart_web()
    print('Restarting Nginx')
    restart_nginx()

def clean_up_docker():
    env.warn_only = True#Allows process to proceed if there is no current container
    run('docker rm -v $(docker ps -a -q -f status=exited)')
    image_clean_result = run('docker rmi $(docker images -f "dangling=true" -q)')
    env.warn_only = False

def deploy_nginx():
    #Restart Nginx
    run("docker pull raybeam/nginx:latest")
    env.warn_only = True#Allows process to proceed if there is no current container
    run('docker rm $(docker stop $(docker ps -a -q --filter name=nginx))')
    env.warn_only = False
#    run("docker run --restart=on-failure -d -p 80:80 -p 443:443 --name=%s_nginx --link %s_flower:flower --link %s_clio_web:clio_web -v ~/.ssl:/etc/ssl/certs/ --volumes-from %s_clio_web intermix/nginx" % (env.environment, env.environment, env.environment, env.environment))
    run("docker run --restart=on-failure -d -v /etc/nginx:/etc/nginx -v /etc/pki/nginx:/etc/pki/nginx -p 80:80 -p 443:443 --link shopping_tool_web:shopping_tool_web --volumes-from shopping_tool_web --name shopping_tool_nginx raybeam/nginx")

def deploy_web_container():
    #Restart UWSGI - Web Server
    run("docker pull allumestyle/catalogue-service:%s" % (env.docker_tag))  # Add Tag
    
    env.warn_only = True #Allows process to proceed if there is no current container
    run('docker rm $(docker stop $(docker ps -a -q --filter name=web))')
    env.warn_only = False

    run("docker run --restart=on-failure -d -v $(pwd)/catalogue_service/settings_local.py:/srv/catalogue_service/catalogue_service/settings_local.py -v ~/static:/srv/catalogue_service/static -p 8000:8000 --name shopping_tool_web --entrypoint=\"/docker-entrypoint-web.sh\" allumestyle/catalogue-service:%s" % (env.docker_tag))



def deploy():
    deploy_web_container()
    deploy_nginx()
    clean_up_docker()
    #deploy_udfs()

    print('deploy complete!')