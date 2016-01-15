#Database adapter
import psycopg2
import os
import pdb

DB_NAME =  os.environ['USER']
DB_HOST =  os.environ['localhost']
DB_PASS =  os.environ['PASSWORD']

#STATEMENTS

CREATE_NODES_TABLE = """
    CREATE TABLE NODES (ID BIGSERIAL PRIMARY KEY  NOT NULL,
    X INT NOT NULL,
    Y INT NOT NULL,
    TYPE TEXT NOT NULL,
    CONTENT JSON  NOT NULL,
    PROJECT INT NOT NULL REFERENCES PROJECTS(ID)
    );"""

CREATE_CONNECTION_TABLE = """
    CREATE TABLE CONNECTIONS (
    ID BIGSERIAL PRIMARY KEY  NOT NULL,
    PROJECT INT NOT NULL REFERENCES PROJECTS(ID),
    TYPE TEXT NOT NULL,
    FROM INT NOT NULL,
    TO INT NOT NULL,
    METADATA JSON
    );
"""

CREATE_USERS_TABLE    = """
    CREATE TABLE USERS (ID BIGSERIAL PRIMARY KEY NOT NULL,
    GOOGLEID TEXT NOT NULL,
    NAME TEXT
    );"""

CREATE_PROJECTS_TABLE = """
    CREATE TABLE PROJECTS (ID BIGSERIAL PRIMARY KEY NOT NULL,
    OWNERS INT[] NOT NULL,
    GROUP INT[]
    );"""

GET_NODES_BY_PROJECT  = """
    SELECT * FROM NODES WHERE PROJECT=%s;
"""

GET_CONNECTIONS_BY_PROJECT = """
    SELECT * FROM CONNECTIONS WHERE PROJECT=%s;
"""

VERIFY_USER_IS_PART_OF_PROJECT = """
    SELECT EXISTS (
    SELECT * FROM PROJECTS WHERE %s in OWNERS || MEMBERS;
    );
"""
#first param is nodeid second is the porjet id
VERIFY_NODE_IS_IN_PROJECT = """
    SELECT EXISTS(
    SELECT * FROM NODES WHERE %s=ID AND %s=PROJECT;
    );
"""

CREATE_GRAPH          = """INSERT INTO PROJECTS (OWNERS, MEMBERS) VALUES (%s, %s);"""

INSERT_NODE           = """INSERT INTO NODES (X,Y,TYPE,CONTENT,PROJECTS) VALUES (%s, %s, %s, %s, %s);"""

INSERT_CONNECTION = """INSERT INTO CONNECTIONS (PROJECT, TYPE, FROM, TO, METADATA) VALUES (%s, %s, %s, %s, %s);"""

#both params are node id
DELETE_CONNECTION = """DELETE FROM NODES WHERE %s=ID; DELETE FROM CONNECTIONS WHERE %s in FROM || TO;"""

try:
    conn = psycopg2.connect("dbname='template1' user='%s' host='%s' password='%s'" % (DB_NAME, DB_HOST, DB_PASS))
except:
    print "I am unable to connect to the database"

cur = conn.cursor()

def executeStatement(executableStatement, arguments):
# helper method to execute a query and get responses
    cur.execute(executeStatement, arguments)
    rows = cur.fetchall()
    return rows

def getGraph(id):
#helper returns the json object of the graph
    executeStatement(GET_ROW_BY_USER, (id))
    pdb.set_trace()
    pass

def verifyUserCanRead(userId, projectId):

    pass

def verifyUserCanEdit():
    pass
