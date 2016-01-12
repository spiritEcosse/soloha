__author__ = 'igor'

from fabric.api import local, prefix, run, cd, settings, put
import os
from soloha.settings import BASE_DIR, PROJECT_NAME
from fabric.state import env
from soloha.settings_local import MY_SERVER
env.user = 'root'
env.skip_bad_hosts = True
env.warn_only = False
env.parallel = False
env.shell = "/bin/bash -l -i -c"
REQUIREMENTS_FILE = 'requirements.txt'
media = 'media/'


def deploy():
    """
    deploy project on remote server
    :return:
    """
    local_act()
    remote_act()


def remote_act():
    """
    run remote acts
    :return: None
    """
    with settings(host_string=MY_SERVER['server']):
        with cd(MY_SERVER['path']):
            run("apt-get install libmemcached-dev")
            run("git reset --hard")

            with prefix('source %s' % MY_SERVER['venv']):
                run('pip install -r %s' % REQUIREMENTS_FILE)
                run("./manage.py migrate")
    #             run("./manage.py flush --noinput")
    #             run("./manage.py loaddata db.json")
                run("./manage.py clear_cache")


def local_act():
    """
    prepare deploy
    :return: None
    """
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "%s.settings" % PROJECT_NAME)
    activate_env = os.path.expanduser(os.path.join(BASE_DIR, ".env/bin/activate_this.py"))
    execfile(activate_env, dict(__file__=activate_env))

    # local("find %s -type d -exec sh -c ' ls \"$0\"/*.jpeg 2>/dev/null && jpegoptim --strip-all -v -t \"$0\"/*.jpeg ' {} \;" % BASE_DIR)
    # local("find %s -type d -exec sh -c ' ls \"$0\"/*.jpg 2>/dev/null && jpegoptim --strip-all -v -t \"$0\"/*.jpg ' {} \;" % BASE_DIR)
    # local("find %s -type d -exec sh -c ' ls \"$0\"/*.png 2>/dev/null && optipng -o5 \"$0\"/*.png ' {} \;" % BASE_DIR)
    # local("find %s -type d -exec sh -c ' ls \"$0\"/*.png 2>/dev/null && optipng -o5 \"$0\"/*.png ' {} \;" % os.path.join(BASE_DIR, "static/src/images/"))

    # with settings(host_string=MY_SERVER['server']):
    #     with cd(MY_SERVER['path']):
    #         put(os.path.join(BASE_DIR, media), MY_SERVER['path'])

    # with settings(host_string=PRODUCTION_SERVER['server'], user='clavutic', password='TZa{7i}x5n-y'):
    #     with cd(PRODUCTION_SERVER['path']):
    #         put(os.path.join(BASE_DIR, media), PRODUCTION_SERVER['path'])
    #
    local("./manage.py test")
    # local("grunt default")
    local("./manage.py makemigrations")
    local("./manage.py migrate")
    # local("./manage.py dumpdata --indent 4 --natural-primary --natural-foreign -e contenttypes -e auth.Permission -e sessions -e admin > db.json")
    local('pip freeze > ' + REQUIREMENTS_FILE)
    local("./manage.py collectstatic --noinput -c")
    local("git add .")
    status = local("git status -s", capture=True)

    if status:
        local("git commit -a -F git_commit_message")
        current_branch = local("git symbolic-ref --short -q HEAD", capture=True)

        if current_branch != 'master':
            local("git checkout master")
            local("git merge %s" % current_branch)
            local("git branch -d %s" % current_branch)

        local("git push bit")
        local("git push origin")

