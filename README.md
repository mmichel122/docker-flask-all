
Simple Python Flask Dockerized Application
Build the image using the following command

$ docker build -t flask-app:latest .
Run the Docker container using the command shown below.

$ docker run -d -p 8080:8080 flask-app
The application will be accessible at http:127.0.0.1:8080 or if you are using boot2docker then first find ip address using $ boot2docker ip and the use the ip http://<host_ip>:8080