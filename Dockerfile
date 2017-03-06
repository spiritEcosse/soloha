FROM soloha_base

ARG WORK_DIR
RUN mkdir $WORK_DIR

RUN apt-get install -y \
	libpq-dev \
	python3 \
	python3-dev \
	python3-setuptools \
	python3-pip \
	libevent-dev \
	python-psycopg2 \
	libjpeg-dev \
	gettext \
	libffi-dev

RUN easy_install3 pip

WORKDIR $WORK_DIR
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
