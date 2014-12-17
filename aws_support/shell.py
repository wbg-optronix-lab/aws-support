# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, absolute_import

import os.path

from boto.manage.cmdshell import sshclient_from_instance


class ShellOperations(object):
    """
    Open a shell for a specified EC2 instance.
    """
    def __init__(self, instance, key_path, user_name):
        self.ssh = sshclient_from_instance(instance,
                                           ssh_key_file=key_path,
                                           user_name=user_name)

    def run_command(self, command, verbose=False):
        """
        Run the specified command on the instance. Raises an exception on error.
        """
        output = self.ssh.run(command)
        if verbose:
            print(output)
        return output

    def create_workspace(self, path, name):
        """
        Creates a folder in the specified path. Raises an exception on error.
        """
        sftp_client = self.ssh.open_sftp()
        sftp_client.mkdir(os.path.join(path, name))

    def put_file(self, source, destination):
        """
        Copy a file to the specified path. Raises an exception on error.
        """
        self.ssh.put_file(source, destination)

    def get_file(self, source, destination):
        """
        Retrieve the specified file. Raises an exception on error.
        """
        self.ssh.get_file(source, destination)

    def list_dir(self, directory):
        """
        Return the contents of the specified directory as a list. Raises an
        exception on error.
        """
        return [f for f in self.ssh.listdir(directory)]

    def close(self):
        """
        Closes the ssh connection.
        Currently affected by boto issue #2600, workaround to catch the
        exception and return.
        """
        try:
            self.ssh.close()
        except AttributeError:
            pass

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()
