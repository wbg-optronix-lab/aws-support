from __future__ import print_function, unicode_literals, absolute_import

import datetime
import json
import logging
import os
import sys
import time

import boto.ec2


class EC2_Connection(object):
    """
    Handles connecting to EC2 and handling reservations and instances.
    """

    def __init__(self, ec2_region, aws_access_key_id, aws_secret_access_key):
        self.conn = boto.ec2.connect_to_region(
            ec2_region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key)
    
    def reservation_list(self):
        """
        Returns a list of reservations.
        """
        return self.conn.get_all_reservations()
    
    def instance_list(self):
        """
        Returns a list of all instances.
        """
        return self.conn.get_only_instances()
    
    def get_available_types(self):
        """
        Return a list of all instance types availiable.
        """
        return list(set(i.instance_type for i in self.instance_list()))
    
    def instance_detail_list(self):
        """
        Returns a dictionary mapping instance types to the availiable instance
        ids for that type as a list.
        """
        return {t: [i.id for i in self.instance_list() if i.instance_type == t]
                for t in self.get_available_types()}

    def start_instance(self, instance_id):
        """
        Start the instance with the specified id. Raises an exception on error.
        """
        self.conn.start_instances(instance_ids=instance_id)
    
    def stop_instance(self, instance_id):
        """
        Stop the instance with the specified id. Raises an exception on error.
        """
        self.conn.stop_instances(instance_ids=instance_id)
        
    def instance_uptime(self, instance_id):
        """
        Get the uptime of the instance with the specified id. Raises an
        exception on error.
        """
        instance = self.get_instance(instance_id)
        timestamp = datetime.datetime.strptime(instance.launch_time,
                                               '%Y-%m-%dT%H:%M:%S.%fZ')
        return datetime.datetime.now() - timestamp
        
    def get_instance(self, instance_id):
        """
        Returns the instance with the specified id. Raises an exception on
        error.
        """
        return self.conn.get_only_instances(instance_ids=[instance_id])[0]
