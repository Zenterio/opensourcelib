#!/bin/sh
exec ssh -q -i /etc/hydra/id_rsa -o "UserKnownHostsFile=/etc/hydra/known_hosts" $@
