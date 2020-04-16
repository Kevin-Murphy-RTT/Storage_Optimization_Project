#!/bin/bash
#Salt Module for SCP
#Format: salt.modules.scp_mod.get(remote_path, local_path='', recursive=False, preserve_times=False, **kwargs)

#Define list of servers in wave
servers=(‘ef-wc-ecco-l-stage1-n1’ ‘ef-wc-ecco-l-stage1-n2’)

#Salt SCP Format: salt.modules.scp_mod.get(remote_path, local_path='', recursive=False, preserve_times=False, **kwargs)

salt.modules.scp_mod.get(kmurphy@