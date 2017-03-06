#!/usr/bin/env bash

if [[ $BUILD == true ]]
then
	tasks_grunt.sh
	prepare.sh
fi

if [[ $SKIP_TOX == false ]]
then
    $TOXBUILD=true tox
fi

tox