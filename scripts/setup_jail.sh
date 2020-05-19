#!/bin/bash
#
# Configure the jail using jailkit.
#
PYTHON_PATH=$(which python)
PYTHON_LIB_PATH=$(python -c "import os, inspect; print(os.path.dirname(inspect.getfile(inspect)))")

mkdir -p $JAIL_DIR
/usr/sbin/jk_init -j $JAIL_DIR jk_lsh
/usr/sbin/jk_cp -j $JAIL_DIR $PYTHON_PATH
/usr/sbin/jk_cp -j $JAIL_DIR $PYTHON_LIB_PATH
addgroup -S $JAIL_GROUPNAME
adduser -S $JAIL_USERNAME -G $JAIL_GROUPNAME
jk_jailuser -m -n -j $JAIL_DIR $JAIL_USERNAME

