# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, absolute_import

import os

from boto.s3.connection import S3Connection


class S3FileManager(object):
    """
    Wrapper around boto to perform high level file management tasks.
    Adapeted from github.com/mattnedrich/S3.FMA
    """

    def __init__(self, aws_key, aws_secret, use_ssl):
        self._aws_connection = S3Connection(aws_key,
                                            aws_secret,
                                            is_secure=use_ssl)

    def getFileNamesInBucket(self, aws_bucketname):
        """
        List all files in the s3 bucket.
        """
        if not self._bucketExists(aws_bucketname):
            self._printBucketNotFoundMessage(aws_bucketname)
            return []
        else:
            bucket = self._aws_connection.get_bucket(aws_bucketname)
            return map(lambda aws_file_key: aws_file_key.name, bucket.list())

    def downloadFileFromBucket(self, aws_bucketname, filename,
                               local_download_directory):
        """
        Download the specified file from the bucket to a local directory.
        """
        if not self._bucketExists(aws_bucketname):
            self._printBucketNotFoundMessage(aws_bucketname)
        else:
            bucket = self._aws_connection.get_bucket(aws_bucketname)
            for s3_file in bucket.list():
                if filename == s3_file.name:
                    self._downloadFile(s3_file, local_download_directory)
                    break

    def downloadAllFilesFromBucket(self, aws_bucketname,
                                   local_download_directory):
        """
        Download all files from the bucket to a local directory.
        """
        if not self._bucketExists(aws_bucketname):
            self._printBucketNotFoundMessage(aws_bucketname)
        else:
            bucket = self._aws_connection.get_bucket(aws_bucketname)
            for s3_file in bucket.list():
                self._downloadFile(s3_file, local_download_directory)

    def deleteAllFilesFromBucket(self, aws_bucketname):
        """
        Delete all files from the bucket.
        """
        if not self._bucketExists(aws_bucketname):
            self._printBucketNotFoundMessage(aws_bucketname)
        else:
            bucket = self._aws_connection.get_bucket(aws_bucketname)
            for s3_file in bucket.list():
                self._deleteFile(bucket, s3_file)

    def downloadFilesInBucketWithPredicate(self,
                                           aws_bucketname,
                                           filename_predicate,
                                           local_download_destination):
        """
        Download all files from the bucket whose names satisfy a predicate.
        """
        if not self._bucketExists(aws_bucketname):
            self._printBucketNotFoundMessage(aws_bucketname)
        else:
            bucket = self._aws_connection.get_bucket(aws_bucketname)
            for s3_file in filter(lambda fkey: filename_predicate(fkey.name),
                                  bucket.list()):
                self._downloadFile(s3_file, local_download_destination)

    def deleteFilesInBucketWithPredicate(self, aws_bucketname,
                                         filename_predicate):
        """
        Delete all files from the bucket whose names satisfy a predicate.
        """
        if not self._bucketExists(aws_bucketname):
            self._printBucketNotFoundMessage(aws_bucketname)
        else:
            bucket = self._aws_connection.get_bucket(aws_bucketname)
            for s3_file in filter(lambda fkey: filename_predicate(fkey.name),
                                  bucket.list()):
                self._deleteFile(bucket, s3_file)

    def _bucketExists(self, bucket_name):
        """
        Return if the bucket exists.
        """
        return self._aws_connection.lookup(bucket_name) is not None

    def _printBucketNotFoundMessage(self, bucket_name):
        print("Error: bucket '{name}' not found".format(name=bucket_name))

    def _downloadFile(self, s3_file, local_download_destination):
        full_local_path = os.path.expanduser(
            os.path.join(local_download_destination, s3_file.name))
        try:
            print("Downloaded: {path}".format(path=full_local_path))
            s3_file.get_contents_to_filename(full_local_path)
        except:
            print("Error downloading")

    def _deleteFile(self, bucket, s3_file):
        bucket.delete_key(s3_file)
        print("Deleted: {name}".format(name=s3_file.name))
