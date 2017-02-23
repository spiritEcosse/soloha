FROM themattrix/tox-base

ARG WORK_DIR
RUN mkdir $WORK_DIR
WORKDIR $WORK_DIR

ONBUILD COPY bash requirements*.txt tox.ini $WORK_DIR/
ONBUILD ARG SKIP_TOX=false
ONBUILD ARG BUILD=true
