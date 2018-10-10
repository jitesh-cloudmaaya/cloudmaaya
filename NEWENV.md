# Allume Shopping Tool: Setting up a New Environment

###### [Deploying](DEPLOY.md)


## Deploying the application to a new Environment


### Code Steps
* Add entries in the fabfile.py and the .circleci/config.yml files
* Add the new host name to settings.py under allowed_hosts

### AWS Steps
* Create RDS Instance
    * Create a stage DB snapshot and restore it to this intance
* Create Elastic Search Instance
* Create EC2 Instances (Web, Worker)
* Create Redis instance

### Common Server Steps
* Install Docker
* Create a catalogue_service directory in the home of whichever user you plan on deploying from.
* Create a copy of settings_local.py in the catalogue_service directory and set all config variables
  * Set `DEBUG = True` to help getting started, you can turn it off later
  * Ensure that the `AUTH_EMAIL_KEY` is set correctly to match what the Allume Auth service will be settings as the Auth Key in cookies


### Logstash Server Steps (Worker Server)
* Install Logstash
* Update the logstash.conf file to match something close to what is in `logstash/pipeline/logstash.yml`






