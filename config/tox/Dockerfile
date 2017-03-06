FROM soloha_base

RUN apt-get update && \
    apt-get install -y --no-install-recommends git ca-certificates && \
        git clone https://github.com/yyuu/pyenv.git .pyenv && \
        (cd .pyenv && git checkout v1.0.6) && \
    apt-get purge -y --auto-remove git ca-certificates && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ENV PYENV_ROOT="/.pyenv" \
    PATH="/.pyenv/bin:/.pyenv/shims:$PATH"

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        make \
        build-essential \
        libssl-dev \
        zlib1g-dev \
        libbz2-dev \
        libreadline-dev \
        libsqlite3-dev \
        llvm \
        libncurses5-dev \
        xz-utils \
        wget \
        ca-certificates && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ONBUILD COPY python-versions.txt ./
ONBUILD RUN xargs -P 4 -n 1 pyenv install < python-versions.txt && \
            pyenv global $(pyenv versions --bare) && \
            find $PYENV_ROOT/versions \
                -type d '(' -name '__pycache__' -o -name 'test' -o -name 'tests' ')' -exec rm -rfv '{}' + && \
            find $PYENV_ROOT/versions -type f '(' -name '*.py[co]' -o -name '*.exe' ')' -exec rm -fv '{}' +

ONBUILD RUN pyenv local 3.6.0 && \
    python -m pip install -U pip && \
    python -m pip install tox && \
    pyenv local --unset && \
    pyenv rehash

RUN 
ARG WORK_DIR
RUN mkdir $WORK_DIR
WORKDIR $WORK_DIR

ONBUILD COPY bash_scripts $WORK_DIR
ONBUILD COPY requirements.txt tox.ini $WORK_DIR/
ONBUILD ARG SKIP_TOX=false
ONBUILD ARG BUILD=true
