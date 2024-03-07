from flaskApi import app

from cloudSql import connectCloudSql
from utils import *
from sqlalchemy import Table, Column, String, Integer, MetaData, insert, select
import models

from utils import engine

# Remove Later
class User():
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    email = Column(String(50))


metaData = MetaData()
table = Table('testTable', metaData,
            Column('id', Integer(), primary_key=True),
            Column('name', String(50), nullable=False),
            Column('email', String(50), nullable=False),
            )

# Remove Later for testing
@app.route('/createTable')
def createTable():
    engine = connectCloudSql()
    
    models.Comment.metadata = models.Base.metadata

    models.Comment.metadata.create_all(engine)
    models.User.metadata = models.Base.metadata
    models.User.metadata.create_all(engine)
    models.UserProjectRelation.metadata = models.Base.metadata
    models.UserProjectRelation.metadata.create_all(engine)
    #metaData.create_all(engine)
    print("Table was created")
    return "Created Table"

@app.route('/dropUserProjectRelationTable')
def dropUserProjectRelationTable():
    models.UserProjectRelation.__table__.drop(engine)
    return True

@app.route('/insert')
def testInsert():
    #engine = connectCloudSql()
    with engine.connect() as conn:
        stmt = insert(table).values(name="PungeBob", email="testEmail@gmail.com")

        conn.execute(stmt)
        conn.commit()

    return "tested"

@app.route('/testGrabData')
def grabData():
    #engine = connectCloudSql()

    with engine.connect() as conn:
        stmt = select(table).where(table.c.email == "testEmail@gmail.com")

        result = conn.execute(stmt)
        result = result.mappings().all()

        retArray = []
        # Recreate Dict from SQLAlchemy Row and return
        # Can't Find any alternatives that worked rn maybe in future
        for row in result:
            d = {}
            d["id"] = row.id
            d["name"] = row.name
            d["email"] = row.email

            retArray.append(d)

    returnArray = {
        "success": True,
        "reason": "",
        "body": retArray,
    }
    
    return returnArray
# End Remove later

# Takes in json with "code" section
@app.route('/api/sendData', methods=["POST"])
def sendData():
    inputBody = request.get_json()

    # Check valid request json
    if "credential" not in inputBody or "code" not in inputBody:
        return { "success": False,
                "reason": "Invalid JSON Provided",
                "body": {}
        }
    
    return { "success": True,
            "reason": "N/A",
            "body": inputBody
            }
