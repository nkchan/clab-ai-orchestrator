#!/bin/bash
docker exec -i vjunos-modifier bash -c 'cat << "EOF" > /tmp/modifier.sh
export LIBGUESTFS_BACKEND=direct
guestfish -a /images/vJunos-router-25.4R1.12.qcow2 -m /dev/sda2 <<_EOF_
download /home/pfe/junos/start-junos.sh /tmp/start-junos.sh
! sed -i "s/grep -ci vmx/grep -iE \\"vmx|svm\\"/g" /tmp/start-junos.sh
upload /tmp/start-junos.sh /home/pfe/junos/start-junos.sh
chmod 0755 /home/pfe/junos/start-junos.sh
exit
_EOF_
EOF
chmod +x /tmp/modifier.sh
/tmp/modifier.sh'
