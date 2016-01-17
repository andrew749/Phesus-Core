#Database adapter
import psycopg2
import os
import json
import pdb

DB_NAME =  'phesus'
DB_USER = 'dummy'
DB_PASS = 'dummy'
DB_HOST = 'localhost'

class NodeType:
    NORMAL = "normal"
    DIAMOND = "diamond"
class ConnectionType:
    NORMAL = "normal"
    BIDIRECTIONAL = "bi"



#STATEMENTS
CREATE_NODES_TABLE = """
    CREATE TABLE IF NOT EXISTS NODES (ID BIGSERIAL PRIMARY KEY  NOT NULL,
    X INT NOT NULL,
    Y INT NOT NULL,
    TYPE TEXT NOT NULL,
    CONTENT JSON  NOT NULL,
    PROJECT INT NOT NULL REFERENCES PROJECTS(ID)
    );"""
CREATE_CONNECTION_TABLE = """
    CREATE TABLE IF NOT EXISTS CONNECTIONS (
    ID BIGSERIAL PRIMARY KEY  NOT NULL,
    PROJECT INT NOT NULL REFERENCES PROJECTS(ID),
    TYPE TEXT NOT NULL,
    FROMNODE INT NOT NULL,
    TONODE INT NOT NULL,
    METADATA JSON
    );
"""
CREATE_USERS_TABLE    = """
    CREATE TABLE IF NOT EXISTS USERS (ID BIGSERIAL PRIMARY KEY NOT NULL,
    NAME TEXT
    );"""
CREATE_PROJECTS_TABLE = """
    CREATE TABLE IF NOT EXISTS PROJECTS (ID BIGSERIAL PRIMARY KEY NOT NULL,
    OWNERS INT[] NOT NULL,
    MEMBERS INT[]
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
CREATE_USER = """INSERT INTO USERS (NAME) VALUES (%s) RETURNING ID;"""
CREATE_GRAPH = """INSERT INTO PROJECTS (OWNERS, MEMBERS) VALUES (%s, %s) RETURNING ID;"""
CREATE_NODE = """INSERT INTO NODES (X,Y,TYPE,CONTENT,PROJECT) VALUES (%s, %s, %s, %s, %s) RETURNING ID;"""
CREATE_CONNECTION = """INSERT INTO CONNECTIONS (PROJECT, TYPE, FROMNODE, TONODE, METADATA) VALUES (%s, %s, %s, %s, %s) RETURNING ID;"""
DELETE_NODE = """DELETE FROM NODES WHERE %s=ID; DELETE FROM CONNECTIONS WHERE %s in FROMNODE || TONODE;""" #both params are node id, when you delete a node all refs are invalid
DELETE_CONNECTION = """DELETE FROM CONNECTIONS WHERE %s = ID; """

#database connection code
try:
    conn = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s'" % (DB_NAME,DB_USER, DB_HOST, DB_PASS))
    cur = conn.cursor()
except:
    print ("Unable to connect")


def initTables():
    #initializes tables if they dont already exist
    executeStatement(CREATE_PROJECTS_TABLE, None, False)
    executeStatement(CREATE_NODES_TABLE, None, False)
    executeStatement(CREATE_USERS_TABLE, None, False)
    executeStatement(CREATE_CONNECTION_TABLE, None, False)

def executeStatement(executableStatement, arguments, getResult):
    # helper method to execute a query and get responses
    if (arguments is not None):
        cur.execute(executableStatement, arguments)
    else:
        cur.execute(executableStatement)
    conn.commit()
    if getResult:
        rows = cur.fetchall()
        return rows

def getGraph(userId, projectId):
#helper returns the json object of the graph
    if(verifyUserCanRead(userId, projectId)):
        nodes = getNodesByProject(userId, projectId)
        connections = getConnectionsByProject(userId, projectId)
        return json.dumps({"projectId":projectId,"nodes":nodes, "connections":connections})
    else:
        return None

def getNodesByProject(userId, projectId):
    #return an array of nodes for the project
    return executeStatement(GET_NODES_BY_PROJECT,  (projectId,), True)

def getConnectionsByProject(userId, projectId):
    #return all the edges of the graph
    return executeStatement(GET_CONNECTIONS_BY_PROJECT, (projectId,), True)

def createGraph(owners, members):
    #return projectId
    return executeStatement(CREATE_GRAPH, (owners, members), True)[0][0]

def createNode(x, y, type, contentJson, projects):
    return executeStatement(CREATE_NODE, (x, y, type, contentJson, projectId), True)

def createUser(name):
    #creats a user and returns the id
    return executeStatement(CREATE_USER, (name,), True)[0][0]

def createConnection(projectId, type, fromnode, tonode, metadata):
    #create a connection and return the id
    return executeStatement(CREATE_CONNECTION, (projectId, type, fromnode, tonode, metadata), True)

def deleteNode(nodeId):
    executeStatement(DELETE_NODE, (nodeId, nodeId), False)

def deleteConnection(connectionId):
    executeStatement(DELETE_CONNECTION, (connectionId), False)

#TODO work on permissions
def verifyUserCanRead(userId, projectId):
    #return boolean if the user can ready
    return True

def verifyUserCanEdit(userId, projectId):
    #verify is a user has read permissions on a graph
    return True


#START OF PROGRAM
initTables()
# id = createUser("John Cena")
# projectId = createGraph([id], [])
# createNode(10, 10, NodeType.NORMAL, json.dumps({"test":"test"}), projectId)
# createConnection(projectId,ConnectionType.BIDIRECTIONAL, id, id - 1, json.dumps({"test":"TEST"}))
print (getGraph(id, 9))
