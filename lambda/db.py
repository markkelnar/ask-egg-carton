# Use this code snippet in your app.
# If you need more information about configurations or implementing the sample code, visit the AWS docs:   
# https://aws.amazon.com/developers/getting-started/python/

import boto3
import base64
from botocore.exceptions import ClientError

import logging
import psycopg2
import traceback
from os import environ

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class DatabaseThing:

    def __init__(self):
        self.endpoint = environ.get('DB_ENDPOINT')
        self.port = environ.get('DB_PORT')
        self.database = environ.get('DB_DATABASE')
        self.dbuser = environ.get('DB_USER')
        self.password = environ.get('DB_PASSWORD')
        self.connection = None


    def connect(self):
        connection_str = "host={0} dbname={1} user={2} password={3} port={4}".format(
            self.endpoint, self.database, self.dbuser, self.password, self.port)
        self.connection = psycopg2.connect(connection_str)
        self.connection.autocommit = True
        return self.connection


    def disconnect(self):
        try:
            self.connection.close()
            self.connection = None
        except:
            pass


    def insert_eggs(self, number, user_id):
        try:
            self.connect()
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO eggs (collected) VALUES (%s)",
                (number)
            )
            self.connection.commit()

        except (Exception, psycopg2.Error) as error :
            if(self.connection):
                logger.error("Failed to insert record into table", error)


    def average_eggs(self, days=7, user_id):
        try:
            self.connect()
            cursor = self.connection.cursor()

            sql = f""" SELECT
                TRUNC(
                    (sum(b.collected_sum) / {days}),
                    1
                )
                FROM (
                    SELECT sum(collected) as collected_sum
                    FROM eggs
                    WHERE created_on >= NOW() - INTERVAL '{days} DAYS'
                    GROUP BY date_trunc('day', created_on)
                ) b
                """
            cursor.execute(sql)
            return cursor.fetchone()[0]
        except (Exception, psycopg2.Error) as error :
            if(self.connection):
                logger.error("Failed to query record", error)


    def total_eggs(self, user_id):
        try:
            self.connect()
            cursor = self.connection.cursor()

            try:
                query="SELECT sum(collected) FROM eggs"
                cursor.execute(query)
                return cursor.fetchone()[0]
            except:
                logger.error("execute error")
                return "Error execute error"
        except:
            return "exception"
