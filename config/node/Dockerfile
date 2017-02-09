FROM node
WORKDIR /code
COPY package.json .
RUN npm install
RUN npm install -g bower
WORKDIR /code/static
COPY static/bower.json .
RUN bower install --allow-root
