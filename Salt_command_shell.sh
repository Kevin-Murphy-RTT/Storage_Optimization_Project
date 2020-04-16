#!/bin/bash

#Define list of servers in wave
servers=(‘ef-wc-ecco-l-stage1-n1’ ‘ef-wc-ecco-l-stage1-n2’)

#Loop through instances in list
for server in $servers
do
    print "Server: $server" #To keep track of the server in case of error
    #Salt remote run command
    salt cmd.run 'df -h >> $server.info.txt && gluster volume info >> $server.info.txt && gluster volume status >> $server.info.txt && cat /etc/fstab >> $server.info.txt'
    
    #Salt Module for SCP (Format: salt.modules.scp_mod.get(remote_path, local_path='', recursive=False, preserve_times=False, **kwargs)
    # salt.modules.scp_mod.get(remote_path=kmurphy@$server, 
    salt $server scp.get (remote_path=/home/kmurphy/$server.info.txt local_path=/home/kmurphy hostname=$server port=22 auto_add_policy=True username=kmurphy password=eia93mtt)
    print "$server.info.txt file completed."
done


# salt -L foo.bar.baz,quo.qux cmd.run 'ps aux | grep foo'
# salt '*' cmd.run,test.ping,test.echo 'cat /proc/cpuinfo',,foo
# salt '*' pip.install salt timeout=5 upgrade=True