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


    def insert_eggs(self, number):
        try:
            self.connect()
            cursor = self.connection.cursor()

            sql = """ INSERT INTO eggs (collected) VALUES (%d) """
            logger.info(sql)
            data = (number)
            cursor.execute(sql, data)
            self.connection.commit()

        except (Exception, psycopg2.Error) as error :
            if(self.connection):
                logger.error("Failed to insert record into table", error)


    def average_eggs(self, days=7):
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
            data = cursor.fetchone()
            logger.info(f"DATA {data[0]}")
            return data[0]
        except (Exception, psycopg2.Error) as error :
            if(self.connection):
                logger.error("Failed to query record", error)


    def total_eggs(self):
        try:
            self.connect()
            cursor = self.connection.cursor()

            try:
                query="SELECT sum(collected) as sum FROM eggs"
                cursor.execute(query)
                return cursor.fetchone()[0]
            except:
                logger.error("execute error")
                return "Error execute error"
        except:
            return "exception"


    def get_secret(self):

        secret_name = "eggCarton/db"
        region_name = "us-east-1"

        # Create a Secrets Manager client
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=region_name
        )

        # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
        # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        # We rethrow the exception by default.

        try:
            get_secret_value_response = client.get_secret_value(
                SecretId=secret_name
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'DecryptionFailureException':
                # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
                # Deal with the exception here, and/or rethrow at your discretion.
                raise e
            elif e.response['Error']['Code'] == 'InternalServiceErrorException':
                # An error occurred on the server side.
                # Deal with the exception here, and/or rethrow at your discretion.
                raise e
            elif e.response['Error']['Code'] == 'InvalidParameterException':
                # You provided an invalid value for a parameter.
                # Deal with the exception here, and/or rethrow at your discretion.
                raise e
            elif e.response['Error']['Code'] == 'InvalidRequestException':
                # You provided a parameter value that is not valid for the current state of the resource.
                # Deal with the exception here, and/or rethrow at your discretion.
                raise e
            elif e.response['Error']['Code'] == 'ResourceNotFoundException':
                # We can't find the resource that you asked for.
                # Deal with the exception here, and/or rethrow at your discretion.
                raise e
        else:
            # Decrypts secret using the associated KMS CMK.
            # Depending on whether the secret is a string or binary, one of these fields will be populated.
            if 'SecretString' in get_secret_value_response:
                secret = get_secret_value_response['SecretString']
            else:
                decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
                
        # Your code goes here. 