#!/bin/bash
#Salt Module for SCP
#Format: salt.modules.scp_mod.get(remote_path, local_path='', recursive=False, preserve_times=False, **kwargs)

#Define list of servers in wave
SERVERS = [
    'serv1'
]

#Salt SCP Format: salt.modules.scp_mod.get(remote_path, local_path='', recursive=False, preserve_times=False, **kwargs)

salt.modules.scp_mod.get(kmurphy@
