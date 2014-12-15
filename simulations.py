#!/usr/bin/env python
from __future__ import print_function, unicode_literals

# first-party imports
import logging
import os
import sys
import time
import json
import yaml

# private imports
import ec2_metal_ops as metal
import ec2_shell_ops as shell

class Sentaurus_Simulation(object):
    
    def __init__(self, instance, key_path, user_name):
        self.operator = shell.Shell_Operations(instance=instance,
                                               ssh_key_file=key_path,
                                               user_name=user_name)
   
    def preflight(self, workspace, job_id, input_dir):
        try:
            self.operator.create_workspace(workspace, job_id)
            self.operator.run_command('cd {0}/{1}'.format(workspace,
                                                          job_id))
            for i in os.listdir(input_dir):
                self.operator.put_file(i, '{0}/{1}/{2}'.format(workspace,
                                                               job_id, i))
            return
        except Exception as e:
            print(e)
            return
    
    def execute(self, command, runfile):
        try:
            self.operator.run_command('cd {0}/{1}'.format(workspace, job_id))
            self.operator.run_command('{0} {1}'.format(command, runfile))
            return
        except Exception as e:
            print(e)
            return
        
    def postflight(self, workspace, job_id, output_dir):
        try:
            self.operator.run_command('cd {0}'.format(workspace))
            for i in self.operator.list_dir({0}.format(job_id)):
                self.get_file('{0}/{1}'.format(job_id, i),
                              '{0}/{1}'.format(output_dir, i))
            return
        except Exception as e:
            print(e)
            return
