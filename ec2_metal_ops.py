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
        
    def start_instance(self, instance_id):
        try:
            instance = self.conn.start_instances(instance_ids=instance_id)
        except Exception as e:
            print(e)
            return
    
    def stop_instance(self, instance_id):
        try:
            self.conn.stop_instances(instance_ids=instance_id)
        except Exception as e:
            logger.critical("Error stopping instance {0}".format(instance_id))
            logger.error(e)
            return



    