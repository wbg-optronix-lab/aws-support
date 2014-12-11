#!/usr/bin/env python
from __future__ import print_function, unicode_literals

# first-party imports
import logging
import os
import sys
import time
import json

# third-party imports
import boto.ec2

# private imports
import cascading_options as co

class EC2_Connection(object):
    
    def __init__(self, ec2_region, aws_access_key_id, aws_secret_access_key):
        self.conn = boto.ec2.connect_to_region(ec2_region, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    
    def reservation_list(self):
        reservations = self.conn.get_all_reservations()
        return reservations
    
    def instance_list(self):
        instances = self.reservation_list()[0].instances
        return instances
    
    def get_available_types(self):
        instances = self.reservation_list()[0].instances
        keys = []
        for i in instances:
            if i.instance_type not in keys:
                keys.append(i.instance_type)
        return keys
    
    def instance_detail_list(self):
        keys = self.get_available_types()
        instances = self.instance_list()
        instance_dict = {}
        for k in keys:
            instance_dict[k] = []
            for i in instances:
                if i.instance_type == k:
                    instance_dict[k].append(i.id)
        return instance_dict
        
    def start_instance(self, instance_id):
        try:
            instance = self.conn.start_instances(instance_ids=instance_id)
        except Exception as e:
            print(e)
            return
    
    def stop_instance(self, instance_id):
        try:
            instance = self.conn.stop_instances(instance_ids=instance_id)
        except Exception as e:
            print(e)
            return
