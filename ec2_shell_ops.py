#!/usr/bin/env python
from __future__ import print_function, unicode_literals

# first-party imports
import logging
import os
import sys
import time
import json

# third-party imports
from boto.manage.cmdshell import sshclient_from_instance

# private imports
import ec2_metal_ops as metal

class Shell_Operations(object):
    
    def __init__(self, instance, key_path, user_name):
        self.ssh = sshclient_from_instance(instance, ssh_key_file=key_path, user_name=user_name)
    
    def run_command(self, command):
        try:
            output = self.ssh.run(command)
            print(output)
        except Exception as e:
            print(e)
            return

    def create_workspace(self, path, name):
        try:
            output = self.ssh.run('mkdir {0}/{1}'.format(path, name))
            print(output)
        except Exception as e:
            print(e)
            return
        
    def put_file(self, source, destination):
        try:
            output = self.ssh.put_file(source, destination)
            print(output)
        except Exception as e:
            print(e)
            return
        
    def get_file(self, source, destination):
        try:
            output = self.ssh.get_file(source, destination)
            print(output)
        except Exception as e:
            print(e)
            return        
        
    def list_dir(self, directory):
        try:
            tmp = []
            for i in self.ssh.listdir(directory):
                tmp.append(i)
            return tmp
        except Exception as e:
            print(e)
            return        

    def close(self):
        self.ssh.close()
        