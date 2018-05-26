#
# Scsr-API Dockerfile
#
#

# Pull base image.
FROM python:3.6

# Get some custom packages
RUN apt-get update && apt-get install -y \
    build-essential \
    make \
    gcc \
    python3-dev \
    mongodb

## make a local (in container) directory
RUN mkdir /opt/scsr-api

# set the working directory (in container)
WORKDIR /opt/scsr-api

# copy all the files in this (current, not container) directory to current container directory (workdir)
ADD . .

# pip install the requirements
RUN pip install -r requirements.txt

# Listen to port 5000 at runtime
EXPOSE 5000

# start the flask app server
CMD python scsr_api/manage.py runserver

