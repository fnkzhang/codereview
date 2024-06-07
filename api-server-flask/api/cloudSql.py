from google.cloud.sql.connector import Connector, IPTypes

import sqlalchemy
from sqlalchemy import Table, Column, String, Integer, Float, Boolean, MetaData, insert, select, update, delete, DateTime, Text
import pymysql

from sqlalchemy.orm import sessionmaker
from dotenv import dotenv_values

import os


def connectCloudSql() -> sqlalchemy.engine.base.Engine:
    config = dotenv_values('.env')

    instance_connection_name = config["INSTANCE_CONNECTION_NAME"]

    db_user =  config["DB_USER"]
    db_pass =  config["DB_PASS"]
    db_name =  config["DB_NAME"]

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config["GOOGLE_APPLICATION_CREDENTIALS"]
    os.environ["GCLOUD_PROJECT"] = config["GCLOUD_PROJECT"]


    print(instance_connection_name, db_user, db_pass, db_name)


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
        pool_size=2000
        #echo = True
    )
    print("Finished Connecting")
    return pool

engine = connectCloudSql()
Session = sessionmaker(engine) # https://docs.sqlalchemy.org/en/20/orm/session_basics.html

