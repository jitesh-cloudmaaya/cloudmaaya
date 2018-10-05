# Allume Shopping Tool


## Deploying the application
The application is automatically deployed through an integration with CircleCI.  This integration is configured in two parts:

### CircleCI
CircleCI is responsible for automated deploys, it is currently configured to test all branches, if the branch is "master" or "develop" and the test pass it will then kick off the deploy process via fab.

The Circle CI config file can be found at: `.circleci/config.yml`

CircleCI USES DEPLY SSH KEYS

#### The steps to a full deploy are:
* Check out Code
* Build a Docker Image with the Code
* Run the Tests in the image
* If the test pass
  * push the image to Docker Hub tagged with the branch name
  * kick off the appropriate deploy process with fabric, passing in config variables 

### Fabric
Fabric is the automation framework we use to run remote tasks on the server, its documentation can be found here http://www.fabfile.org/:

The fabric config file can be found in the root directory: `fabfile.py`

The fabfile will deploy to its target env with the fab command followed by the env name and then deploy, you can optionally include a docker tag to override the default docker tag name for the QA (Stage) and UAT environments, otherwise both default to develop.

e.g. `fab qa deploy docker_tag=featurerotate_collage_products`

Note: the slashes in beween feature and teh feature name from the git branch are automatically removed as docker tagging does not support them

### Deploy Process:
* Set Up Env Variables
* Set Hosts (Web, Worker)
* SSH into hosts
* Pull latest images with the correct docker tag (e.g. develop)
* Restart Instances
  * Kill existing instances
  * Start new instances with new image



