#!/usr/bin/env bash
current_dir := $(notdir $(CURDIR))
solr_version := 4.10.2
#solr_version := 6.3.0
solr := solr
solr_file := $(solr)-$(solr_version)
opt_solr := /opt/$(solr)
schema_xml := "$(opt_solr)/solr/$(current_dir)/conf/schema.xml"
jetty := jetty

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
	sudo -u postgres psql -c "CREATE USER $(current_dir) WITH PASSWORD '$(current_dir)';"

    # Grant privileges
	sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $(current_dir) TO $(current_dir);"

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

	# Todo Move this to doc
	# If use pycharm: add /usr/local/lib/node_modules/grunt-cli/ to Grunt Task in input - grunt cli package

install_pip:
	sudo apt-get install python-pip
	sudo pip install virtualenvwrapper

virtual_environment:
	# Create virtualenv and install libs from requirements
	./venv.sh $(current_dir)

create_settings_local:
    # Create settings_local
	cp $(current_dir)/settings_sample.py $(current_dir)/settings_local.py

debian_ubuntu_install_modules: postgresql libs install_pip

site: debian_ubuntu_install_modules create_settings_local solr virtual_environment

solr: solr_remove install_solr

install_solr:
#	sudo apt-get install python-software-properties
#	sudo add-apt-repository ppa:webupd8team/java
#	sudo apt-get update
#	sudo apt-get -y install oracle-java8-installer
#	sudo mkdir /usr/java
#	sudo mkdir $(opt_solr)
	sudo ln -sf /usr/lib/jvm/java-8-openjdk-amd64 /usr/java/default
	sudo wget -P /opt https://archive.apache.org/dist/lucene/$(solr)/$(solr_version)/$(solr_file).tgz
	sudo tar -xvf /opt/$(solr_file).tgz
	sudo cp -R /opt/$(solr_file)/example $(opt_solr)
	sudo apt-get install jetty
	sudo cp -f $(solr)/$(jetty) /etc/default/$(jetty)
	sudo useradd -d $(opt_solr) -s /sbin/false $(solr)
	sudo chown $(solr):$(solr) -R $(opt_solr)
	sudo mv $(opt_solr)/solr/collection1 $(current_dir)
	sudo rm -R $(opt_solr)/solr/$(current_dir) data
	sudo echo "name=$(current_dir)" > $(opt_solr)/solr/$(current_dir)/core.properties

	./manage.py build_$(solr)_schema > $(schema_xml)
	sudo chown $(solr):$(solr) -R /opt/$(solr)/*
	sudo service $(jetty) start

solr_remove: solr_remove_service solr_remove_folders

solr_remove_service:
#	sudo service $(jetty) stop
	sudo rm -f /etc/default/$(jetty).in.sh
	sudo rm -fr /etc/init.d/$(jetty)

solr_remove_folders:
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
