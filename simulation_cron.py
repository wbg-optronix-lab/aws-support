import os
import time
import yaml
import json
import datetime

import cascading_options as co

import ec2_metal_ops as metal
import ec2_shell_ops as shell
import simulations as sims


class TaskRun(object):
    
    def __init__(self):
        
        self.signals = metal.EC2_Connection(ec2_region, aws_access_key_id, aws_secret_access_key)
        self.terminal = shell.Shell_Operations(instance, key_path, user_name)
        self.todo = requests.get(url, headers={'Authorization': auth_token}).json()['results']
    
    def get_sims_todo(self):
        todo_list = {}
        for i in self.signals.instance_list:
            if not todo_list[i.instance_type]:
                todo_list[i.instance_type] = []
                for task in self.todo:
                    if task.execution_node == i.instance_type:
                        todo_list[i.instance_type].append(task)
        return todo_list
    
    def get_instances_uptime(self):
        uptimes = {}
        for i in self.signals.instance_list:
            uptimes[i.id] = self.signals.instance_uptime(i.id)
        return uptimes
    
    def runner(self):
        
        todo_list = self.get_sims_todo()
        for i in self.signals.instance_list():
            if i.status == 'running':
                if self.get_sims_todo()[i.instance_type] == 0:
                    if self.signals.get_instance_uptime(i.id) >= 50: #check time formatting, REMAINDER!!!
                        self.signals.stop_instance(i.id)
                else:
                    for task in self.get_sims_todo()[i.instance_type]:
                        s = sims.Sentaurus_Simulation(i.id, self.key_path, self.user_name)
                        s.preflight()
                        s.execute()
                        s.postflight()
                        response = requests.post(url, data=DATA, headers={'Authorization': auth_token})
            elif i.status == 'stopped':
                if self.get_sims_todo()[i.instance_type] >= 1:
                    self.signals.start_instance(i.id)
                    time.sleep(60)
                    for task in self.get_sims_todo()[i.instance_type]:
                        s = sims.Sentaurus_Simulation(i.iid, self.key_path, self.user_name)
                        s.preflight()
                        s.execute()
                        s.postflight()
                        response = requests.post(url, data=DATA, headers={'Authorization': auth_token})
        

if __name__ == '__main__':
    
    parse = co.cascading_parser()
    parse.add_argument('--region', metavar='ec2_region', help='EC2 Region')
    parse.add_argument('--aws_key', metavar='aws_key', help='AWS Key')
    parse.add_argument('--aws_secret', metavar='aws_secret', help='AWS Secret')
    parse.add_argument('--url', metavar='url', help='REST URL')
    parse.add_argument('--token', metavar='token', help='Auth Token')
    parse.add_argument('--dry_run', metavar='store_true', default=False,
                       help='turns off database update')
    parse.add_argument('--log_file', metavar='filename', default='log.txt',
                       help='file to log to')
    parse.add_argument('--log_level', metavar='level', default='error',
                       help='sets logging level for the file')

    parser = parse.cascade_options()
    
    c = TaskRun
    c.runner()
