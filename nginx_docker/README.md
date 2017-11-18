# CLIO Nginx Docker Image

Building the Image:
docker build -t intermix/nginx .

Running the Image:
The SSL cert and key need to be symlinked into /etc/ssl/certs
  - intermix_bundle.crt;
  - intermix.io.key;

