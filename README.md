
![Catalog Service](/gimbels.jpg)


# Allume Shopping Tool

###### [Deploying](DEPLOY.md)
###### [Creating New Environments](NEWENV.md)

## Application Details
This is a Django Project

### Web Server
* Development - Django Builtin
* Production - uWSGI

### Data Backend 
* Database: MySQL 
* Search Store: Elastic Search

### Jobs Server
* Celery
* Redis (Elasticache - Redis_)

### Indexing Pipeline - Logstash
[Logstash Config](https://qbox.io/blog/migrating-mysql-data-into-elasticsearch-using-logstash)


### Background Workers
Celery


## Development (OSX)
### You will need to install mysql:
https://gist.github.com/nrollr/3f57fc15ded7dddddcc4e82fe137b58e

### Install VirtualEnv
`brew install python`

### Install wkhtmltopdf
`brew install Caskroom/cask/wkhtmltopdf`

### Create a new Virtual Env for the project, the command below puts it in a folder in your home folder if you have another then use that :
`virtualenv ~/VENV/catalogue_service`

### Activate the Virtual Env:
Requires Python 2.7
`source ~/VENV/catalogue_service/bin/activate`

### From the repo folder install the requirements:
Requires pip 10.01
`pip install -r requirements`

### Once you have mysql installed and have the mysql root password all set run:
`mysql -u root -e "CREATE DATABASE catalogue_service"`

### After that run the DB migrations to set up the DB:
`python manage.py migrate`

### Start the Webserver:
`python manage.py runserver`

### The current client homepage is:
http://127.0.0.1:8000/[STYLING SESSION ID]

### AUTH Workaround for local Development
Auth requires connecting to the Allume Auth service, which will likely not be running locally.  There are two work arounds:

#### Setting Cookies Locally
The settings_local.py file has a key `DEV_AUTH_EMAIL`
You can set that to any user_email from the wp_users tables and then my point your browser to /set_cookie on your local web server, from there the Auth cookie will be set and you can then point your browser to a styling session.

#### Hosts File
Alterntaively you can set the `AUTH_LOGIN_URL` and `AUTH_EMAIL_KEY` keys and use the Allume Auth service, your browser will be redirected to the Auth service, e.g. 'https://social-services-stage.allume.co/auth/oauth/login/google-oauth2/' which will set a cookie on your local browser.  

For your your local dev app server to be able to read the cookies that was set you will need to create an entry in your hosts file, e.g. /etc/hosts for:
    shopping-tool-web-dev.allume.co  127.0.0.1  

Once you have that in place use will need to accesss the app from https://shopping-tool-web-dev.allume.co

