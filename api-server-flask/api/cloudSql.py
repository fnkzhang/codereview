from google.cloud.sql.connector import Connector, IPTypes

import sqlalchemy
from sqlalchemy import Table, Column, String, Integer, Float, Boolean, MetaData, insert, select, update, delete, DateTime, Text

import pymysql

from sqlalchemy.sql import func
from sqlalchemy.orm import sessionmaker

import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials/googlecreds.json"
os.environ["GCLOUD_PROJECT"] = "codereview-413200"
CLIENT_ID = "474055387624-orr54rn978klbpdpi967r92cssourj08.apps.googleusercontent.com"

def connectCloudSql() -> sqlalchemy.engine.base.Engine:
    instance_connection_name = "codereview-413200:us-central1:cr-cloudsql-db"
    db_user = "root"
    db_pass = "Q$mXxb?_io-#<-_0"
    db_name = "test"

    ip_type = IPTypes.PUBLIC

    connector = Connector(ip_type)

    def getconn() -> pymysql.connections.Connection:
        conn: pymysql.connections.Connection = connector.connect(
            instance_connection_name,
            "pymysql",
            user=db_user,
            password=db_pass,
            db=db_name,
        )
        
        return conn;

    pool = sqlalchemy.create_engine(
        "mysql+pymysql://",
        creator=getconn,
        #echo = True
    )
    print("Finished Connecting")
    return pool

engine = connectCloudSql()
Session = sessionmaker(engine) # https://docs.sqlalchemy.org/en/20/orm/session_basics.html

