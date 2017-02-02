#!/usr/bin/env bash
current_dir := $(notdir $(CURDIR))

postgresql:
    # Install postgresql
	sudo apt-get install postgresql postgresql-contrib

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
	sudo apt install npm
	sudo npm install -g less
	sudo ln -sf /usr/bin/nodejs /usr/bin/node

    # Install bower
	sudo npm install -g bower

    # Install bower components
	cd static && bower install

    # Install other libs
	sudo apt-get install libpq-dev
	sudo apt-get install libmagickwand-dev
	sudo apt-get install libjpeg-dev

    # Install gettext for run makemessages
	sudo apt-get install gettext

	sudo apt-get install libffi-dev

	# Install grunt
	sudo npm install -g grunt-cli

	# Install npm libs
	npm install

	# Docker
	sudo apt install -y docker-compose

	# Todo Move this to doc
	# If use pycharm: add /usr/local/lib/node_modules/grunt-cli/ to Grunt Task in input - grunt cli package

install_pip:
	sudo apt-get install python-pip
	sudo pip install virtualenvwrapper

virtual_environment:
	# Create virtualenv and install libs from requirements
	./venv.sh $(current_dir)

virtual_environment_docker3:
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
	docker run -a stdin -a stdout -i -t soloha_web /bin/bash




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
