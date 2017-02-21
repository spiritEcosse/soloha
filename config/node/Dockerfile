FROM node

ARG WORK_DIR
ARG STATIC_FOLDER
WORKDIR $WORK_DIR

COPY package.json .
RUN npm install -g bower
RUN npm install -g grunt-cli

COPY bower.json .

COPY Gruntfile.coffee .
COPY $STATIC_FOLDER .
