
![Catalog Service](/gimbels.jpg)


# Allume Shopping Tool


## Application Details
This is a Django Project

### Web Server
* Development - Django Builtin
* Production - uWSGI

### Data Backend 
* Database: MySQL 
* Search Store: Elastic Search

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

### Create a new Virtual Env for the project, the command below puts it in a folder in your home folder if you have another then use that:
`virtualenv ~/VENV/catalogue_service`

### Activate the Virtual Env:
`source ~/VENV/catalogue_service/bin/activate`

### From the repo folder install the requirements:
`pip install -r requirements`

### Once you have mysql installed and have the mysql root password all set run:
`mysql -u root -e "CREATE DATABASE catalogue_service"`

### After that run the DB migrations to set up the DB:
`python manage.py migrate`

### Start the Webserver:
`python manage.py runserver`

### The current client homepage is:
http://127.0.0.1:8000/shopping_tool/

### The API accepts a single query parameter right now and paging, e.g.:
http://127.0.0.1:8000/product_api/facets?text=jeans&page=2&num_per_page=10

