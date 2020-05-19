#!/bin/bash
#
# Download, build, and install jailkit.
#
#
JAIL_VER=jailkit-2.20

wget http://olivier.sessink.nl/jailkit/${JAIL_VER}.tar.gz
tar -xzvf ${JAIL_VER}.tar.gz
chmod -R 777 $JAIL_VER/py
2to3 -w $JAIL_VER/py/jk_addjailuser.in
2to3 -w $JAIL_VER/py/jk_check.in
2to3 -w $JAIL_VER/py/jk_cp.in
2to3 -w $JAIL_VER/py/jk_init.in
2to3 -w $JAIL_VER/py/jk_jailuser.in
2to3 -w $JAIL_VER/py/jk_lib.py
2to3 -w $JAIL_VER/py/jk_list.in
2to3 -w $JAIL_VER/py/jk_update.in
sed -i 's/string\./str\./g' $JAIL_VER/py/jk_lib.py
sed -i 's/line = p.stdout.readline()/lin = p.stdout.readline();line = lin.decode()/g' $JAIL_VER/py/jk_lib.py
sed -i 's/^.*jk_lib\.pyc.*//g' $JAIL_VER/py/Makefile.in

cat > $JAIL_VER/ini/jk_init.ini <<EOL
[jk_lsh]
comment = Jailkit limited shell
paths = /etc/localtime, /usr/sbin/jk_lsh, /etc/jailkit/jk_lsh.ini, /lib/libnsl.so.1, /lib64/libnsl.so.1, /lib/libnss*.so.2, /lib64/libnss*.so.2, /lib/i386-linux-gnu/libns
users = root
groups = root
need_logsocket = 1
EOL

pushd $JAIL_VER
./configure && make && make install
popd

# cleanup
rm -fr $JAIL_VER
rm -f ${JAIL_VER}.tar.gz

