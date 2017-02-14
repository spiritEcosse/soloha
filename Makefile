#!/usr/bin/env bash
current_dir := $(notdir $(CURDIR))
solr_version := 4.10.2
#solr_version := 6.3.0
solr := solr
opt := /opt/
solr_file := $(solr)-$(solr_version)
opt_solr := /opt/$(solr)
schema_xml := $(opt_solr)/solr/$(current_dir)/conf/schema.xml
jetty := jetty
jetty-v := $(jetty)8
jetty_logging := $(jetty)-logging.xml
jetty_version := 9.4.0.v20161208
multicore_solr := $(opt_solr)/multicore/$(solr).xml
data_solr := $(opt_solr)/$(solr)/$(current_dir)/data

postgresql:
    # Install postgresql
	sudo apt-get -y install postgresql postgresql-contrib

    # Restart postgresql
	sudo service postgresql restart

    # Drop db:
	sudo -u postgres dropdb $(current_dir) --if-exists

	# Create db:
	sudo -u postgres createdb $(current_dir)

    # Drop user
	sudo -u postgres dropuser $(current_dir) --if-exists

    # Create user
	sudo -u postgres psql -c "CREATE USER $(current_dir) WITH PASSWORD '$(current_dir)' SUPERUSER;"

libs:
    # Install compiler from less to css
	sudo apt -y install npm
	sudo npm install -g less
	sudo ln -sf /usr/bin/nodejs /usr/bin/node

    # Install bower
	sudo npm install -g bower

    # Install bower components
	cd static && bower install

    # Install other libs
	sudo apt-get -y install libpq-dev
	sudo apt-get -y install libmagickwand-dev
	sudo apt-get -y install libjpeg-dev

    # Install gettext for run makemessages
	sudo apt-get -y install gettext

	sudo apt-get -y install libffi-dev

	# Install grunt
	sudo npm install -g grunt-cli
	npm install grunt-cli

	# Install npm libs
	npm install

	# Docker
	sudo apt install -y docker-compose

	# Todo Move this to doc
	# If use pycharm: add /usr/local/lib/node_modules/grunt-cli/ to Grunt Task in input - grunt cli package

install_pip:
	sudo apt-get -y install python-pip
	sudo pip install virtualenvwrapper

virtual_environment:
	# Create virtualenv and install libs from requirements
	./venv.sh $(current_dir)

create_settings_local:
    # Create settings_local
	cp $(current_dir)/settings_sample.py $(current_dir)/settings_local.py

debian_ubuntu_install_modules: postgresql libs install_pip

initial_db:
	./initial_db.sh $(current_dir)

reset_db: postgresql initial_db

python3:
	sudo apt-get install python3-dev libevent-dev python-psycopg2

docker_python3:
	sudo apt-get install libevent-dev python-psycopg2

site: debian_ubuntu_install_modules create_settings_local virtual_environment
site3: create_settings_local python3 virtual_environment
site_docker3: create_settings_local virtual_environment_docker3
test: run_test


run_test:
	detox



docker_restart_machine:
	docker-machine restart dev
	docker-machine env dev
	eval $(docker-machine env dev)

docker_compose_up: docker_compose_build
	docker-compose up

docker_compose_build:
	docker-compose build

docker_run: docker_restart_machine docker_compose_build docker_compose_up

docker_shell:
	docker exec -it soloha_web_1 bash

docker_compose_kill_rm:
	docker-compose kill web db
	docker-compose rm web db
	docker rmi soloha_web postgres



post_compose_up:
	eval $(docker-machine env dev)
	docker exec soloha_web_1 ./manage.py collectstatic --noinput
	docker exec soloha_web_1 ./manage.py makemigrations
	docker exec soloha_web_1 ./manage.py migrate

	# not test
	docker exec soloha_web_1 ./manage.py loaddata data/fixtures/*.json
	docker exec soloha_web_1 ./manage.py oscar_populate_countries
	docker exec soloha_web_1 ./manage.py rebuild_index


site: debian_ubuntu_install_modules create_settings_local solr virtual_environment
	sudo bash -c "source virtualenvwrapper.sh && workon $(current_dir) && ./manage.py build_$(solr)_schema > $(schema_xml)"


solr: install_java solr_remove install_solr
solr_production: solr_remove install_solr

install_java:
	# For Debian
#	su -
#	echo "deb http://ppa.launchpad.net/webupd8team/java/ubuntu xenial main" | tee /etc/apt/sources.list.d/webupd8team-java.list
#	echo "deb-src http://ppa.launchpad.net/webupd8team/java/ubuntu xenial main" | tee -a /etc/apt/sources.list.d/webupd8team-java.list
#	apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys EEA14886
#	apt-get update
#	apt-get -y install oracle-java8-installer
#	exit
	# end for Debian

#	sudo apt-get -y install python-software-properties # Debian Wheezy and earlier
	sudo apt-get -y install software-properties-common # Debian Jessie and later (2014-)
	sudo add-apt-repository ppa:webupd8team/java -y
	sudo apt-get update
	sudo apt-get -y install oracle-java8-installer
	sudo mkdir -p /usr/java
	sudo ln -sf /usr/lib/jvm/java-8-openjdk-amd64 /usr/java/default

install_solr:
	sudo mkdir $(opt_solr)
	sudo wget -P $(opt) https://archive.apache.org/dist/lucene/$(solr)/$(solr_version)/$(solr_file).tgz
	sudo tar -xvf $(opt)$(solr_file).tgz -C $(opt)
	sudo cp -rp $(opt)$(solr_file)/example/* $(opt_solr)/
	sudo cp -f $(solr)/$(jetty)/$(jetty) /etc/default/$(jetty)
	sudo cp -f $(solr)/$(jetty)/$(jetty_logging) $(opt_solr)/etc/
	sudo useradd -d $(opt_solr) -s /sbin/false $(solr) &>/dev/null
	sudo cp -f $(solr)/$(jetty)/$(jetty).sh /etc/init.d/$(jetty)
	sudo chmod a+x /etc/init.d/$(jetty)
	sudo update-rc.d $(jetty) defaults
	sudo mv $(opt_solr)/$(solr)/collection1 $(opt_solr)/$(solr)/$(current_dir)
	sudo bash -c "echo 'name=$(current_dir)' > $(opt_solr)/$(solr)/$(current_dir)/core.properties"
	sudo rm -fr $(data_solr)
	sudo mkdir $(data_solr) &>/dev/null
	sudo cp -f $(solr)/$(jetty)/start.ini $(opt_solr)
	sudo chown $(solr):$(solr) -R $(opt_solr)/*
	sudo service $(jetty) start
	sudo service $(jetty) restart

solr_remove: solr_remove_service solr_remove_folders

solr_remove_service:
	sudo sudo apt-get --purge remove jetty*
	sudo service $(jetty) stop &>/dev/null
	sudo rm -f /etc/default/$(jetty)*
	sudo rm -f /etc/init.d/$(jetty)*
	sudo rm -fr /var/lib/$(jetty)*

solr_remove_folders:
	sudo rm -fr /opt/$(solr)
	sudo rm -fr /opt/$(solr)*

deluser_solr:
	sudo deluser -f --remove-home solr
	sudo deluser -f --group solr



sandbox_image:
    docker build -t django-oscar-sandbox:latest .

docs:
	cd docs && make html

coverage:
	py.test --cov=oscar --cov-report=term-missing

lint:
	flake8 src/oscar/
	isort -q --recursive --diff src/

testmigrations:
	pip install -r requirements_migrations.txt
	cd sites/sandbox && ./test_migrations.sh

# This target is run on Travis.ci. We lint, test and build the sandbox
# site as well as testing migrations apply correctly. We don't call 'install'
# first as that is run as a separate part of the Travis build process.
travis: install coverage lint build_sandbox testmigrations

messages:
	# Create the .po files used for i18n
	cd src/oscar; django-admin.py makemessages -a

compiledmessages:
	# Compile the gettext files
	cd src/oscar; django-admin.py compilemessages

css:
	npm install
	npm run build

clean:
	# Remove files not in source control
	find . -type f -name "*.pyc" -delete
	rm -rf nosetests.xml coverage.xml htmlcov *.egg-info *.pdf dist violations.txt

preflight: lint
    # Bare minimum of tests to run before pushing to master
	./runtests.py

todo:
	# Look for areas of the code that need updating when some event has taken place (like
	# Oscar dropping support for a Django version)
	-grep -rnH TODO *.txt
	-grep -rnH TODO src/oscar/apps/
	-grep -rnH "django.VERSION" src/oscar/apps


release: clean
	pip install twine wheel
	rm -rf dist/*
	python setup.py sdist bdist_wheel
	twine upload -s dist/*

#./manage.py dumpdata --indent 4 --natural-primary --natural-foreign -e contenttypes -e auth.Permission -e sessions -e admin > data/fixtures/all.json
#for tests :run in shell for webdriver.Firefox():export PATH=$PATH:/home/igor/web/
# run all tests under all envs
#$ tox
#
## run tests under specific env
#$ TOXENV=py34-dj18 tox
#
## run specific test
#$ TOXENV=py34-dj18 tox python manage.py test tests.test_flow_signal.Test.test_signal_usecase
#
## run examples
#$ TOXENV=py34-dj18 tox python manage.py migrate --settings=examples.settings
#$ TOXENV=py34-dj18 tox python manage.py loaddata <path_to_json> --settings=examples.settings
#$ TOXENV=py34-dj18 tox python manage.py runserver --settings=examples.settings
