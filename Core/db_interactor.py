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
    """An enumeration of the different types of nodes."""
    NORMAL = "normal"
    DIAMOND = "diamond"

class ConnectionType:
    """An enumeration of the different types of connections."""
    NORMAL = "normal"
    BIDIRECTIONAL = "bi"

class PermissionType:
    """An enumeration of the different types of access to a project."""
    READ = 1
    WRITE = 2
    READWRITE = 3


#STATEMENTS
CREATE_NODES_TABLE = """
    CREATE TABLE IF NOT EXISTS NODES (
    ID UUID PRIMARY KEY  NOT NULL,
    X INT NOT NULL,
    Y INT NOT NULL,
    TYPE TEXT NOT NULL,
    CONTENT JSON  NOT NULL,
    PROJECT INT NOT NULL REFERENCES PROJECTS(ID)
    );
"""
CREATE_CONNECTION_TABLE = """
    CREATE TABLE IF NOT EXISTS CONNECTIONS (
    ID UUID PRIMARY KEY  NOT NULL,
    PROJECT INT NOT NULL REFERENCES PROJECTS(ID),
    TYPE TEXT NOT NULL,
    FROMNODE INT NOT NULL,
    TONODE INT NOT NULL,
    METADATA JSON
    );
"""
CREATE_USERS_TABLE = """
    CREATE TABLE IF NOT EXISTS USERS (
    ID BIGSERIAL PRIMARY KEY NOT NULL,
    NAME TEXT,
    EMAIL TEXT,
    GOOGLE_ID TEXT
    );
"""
CREATE_PROJECTS_TABLE = """
    CREATE TABLE IF NOT EXISTS PROJECTS (
    ID BIGSERIAL PRIMARY KEY NOT NULL,
    OWNERS INT[] NOT NULL,
    MEMBERS INT[]
    );
"""
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
CREATE_USER = """INSERT INTO USERS (NAME, EMAIL, GOOGLE_ID) VALUES (%s, %s, %s) RETURNING ID;"""
CREATE_GRAPH = """INSERT INTO PROJECTS (OWNERS, MEMBERS) VALUES (%s, %s) RETURNING ID;"""
CREATE_NODE = """INSERT INTO NODES (X,Y,TYPE,CONTENT,PROJECT) VALUES (%s, %s, %s, %s, %s) RETURNING ID;"""
CREATE_CONNECTION = """INSERT INTO CONNECTIONS (PROJECT, TYPE, FROMNODE, TONODE, METADATA) VALUES (%s, %s, %s, %s, %s) RETURNING ID;"""
UPDATE_NODE = """UPDATE NODES SET x = %s, y = %s, type = %s, content = %s,   where ID = %s;"""
UPDATE_CONNECTION = """UPDATE CONNECTIONS SET type = %s, tonode = %s, fromnode = %s, metadata = %s where ID = %s;"""
DELETE_NODE = """DELETE FROM NODES WHERE %s=ID; DELETE FROM CONNECTIONS WHERE %s in FROMNODE || TONODE;""" #both params are node id, when you delete a node all refs are invalid
DELETE_CONNECTION = """DELETE FROM CONNECTIONS WHERE %s = ID; """
CHECK_IF_NODE_IS_IN_PROJECT = """
SELECT EXISTS (
    SELECT * FROM NODES WHERE ID = %s AND project = %s
    );
"""
CHECK_IF_CONNECTION_IS_IN_PROJECT = """
SELECT EXISTS (
    SELECT * FROM CONNECTIONS WHERE ID = %s AND project = %s
    );
"""
CHECK_IF_USER_IS_IN_PROJECT = """
SELECT EXISTS (
    SELECT * FROM PROJECTS WHERE %s=ID AND %s in OWNERS
    );
"""
CHECK_IF_USER_EXISTS = """
SELECT EXISTS(
    SELECT * FROM USERS WHERE %s=ID
);
"""

#Database connection code
try:
    conn = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s'" % (DB_NAME,DB_USER, DB_HOST, DB_PASS))
    cur = conn.cursor()
except:
    print ("Unable to connect")


def initTables():
    """ Initializes tables if they dont already exist."""
    executeStatement(CREATE_PROJECTS_TABLE, None, False)
    executeStatement(CREATE_NODES_TABLE, None, False)
    executeStatement(CREATE_USERS_TABLE, None, False)
    executeStatement(CREATE_CONNECTION_TABLE, None, False)

def executeStatement(executableStatement, arguments, getResult):
    """
    Helper method to execute a query and get responses.
    :param executableStatement: A string of the database query to perform.
    :param arguments: A tuple of the arguments to insert into the executable statement.
    :param getResult: Boolean representing whether or not to return something at the end of the query.
    :return returns the query if specified in getResult
    """
    if (arguments is not None):
        cur.execute(executableStatement, arguments)
    else:
        cur.execute(executableStatement)
    conn.commit()
    if getResult:
        rows = cur.fetchall()
        return rows

def checkIfUserExists(uid=userId):
    return executeStatement(CHECK_IF_USER_EXISTS, (userId), True)

""" Helper functions that decorate other functions,
    can check authentication and read and write
    permissions here.
"""
def CanRead(func):
    """Decorator to wrap functions and restrict access if a user can't read"""
    def i(*args, **kwargs):
        if(checkIfUserExists(kwargs.uid) and verifyUserCanRead(kwargs.uid, kwargs.pid)):
            return func(*args, **kwargs)
        else:
            return json.dumps({"ERROR":"Cannot Read"})
    return i

def CanWrite(func):
    """Same as read but with write permissions"""
    def i(*args, **kwargs):
        if(checkIfUserExists(kwargs.uid) and verifyUserCanEdit(kwargs.uid, kwargs.pid)):
            return func(*args, **kwargs)
        else:
            return json.dumps({"ERROR":"Cannot Write"})
    return i

"""Remaining helper functions to access the db"""

@CanRead
def getNodesByProject(uid=userId,
                      pid=projectId):
    """
    Return an array of nodes for the project.
    :param userId: The id of the user to access the project.
    :param projectId: The id of the project to get the nodes for.
    :return Rows each representing a node of the project.
    """
    return executeStatement(GET_NODES_BY_PROJECT,  (projectId,), True)

@CanRead
def getConnectionsByProject(uid=userId,
                            pid=projectId):
    """
    Return all the edges of the graph.
    :param userId: Id
    :param projectId: Project Id
    """
    return executeStatement(GET_CONNECTIONS_BY_PROJECT, (projectId,), True)

@CanRead
def getProject(uid=userId,
             pid=projectId):
    """
    Helper returns the json object of the graph.
    :param userId: The unique userId.
    :param projectId: The unique id of the project to get.
    :return A dictionary containing the nodes and connections of the project.
    """
    nodes = getNodesByProject(userId, projectId)
    connections = getConnectionsByProject(userId, projectId)
    return json.dumps({"projectId":projectId,"nodes":nodes, "connections":connections})

#Anyone can create a graph
def createGraph(owners=owners,
                members=members):
    """
    Helper to create a graph.
    :param owners: Array of userId's to own the graph.
    :param members: Array of userId's who are associated with the graph.
    :return The new project id.
    """
    return executeStatement(CREATE_GRAPH, (owners, members), True)[0][0]

def createUser(email=email, googleId = gid, name=name):
    """
    A helper to create a user.
    :param name:The name of the user.
    :return The id of the newly created user.
    """
    return executeStatement(CREATE_USER, (name, email, gid), True)[0][0]

@CanWrite
def createNode(x=x,
               y=y,
               type=type,
               content=contentJson,
               pid=projectId):
    """
    A helper to create a node.
    :param x: The x coordinate of the node.
    :param y: The y coordinate of the node.
    :param type: The type of the node to create. See NodeTypes.
    :param contentJson: The content for the node.
    :param projectId: The project that the node is associated with.
    :return The node id of the newly created node.
    """
    return executeStatement(CREATE_NODE, (x, y, type, contentJson, projectId), True)

@CanWrite
def createConnection(pid=projectId,
                     type=type,
                     fromNode=fromnode,
                     toNode=tonode,
                     metadata=etadata):
    """
    A helper to create a connection.
    :param projectId: The id of the project associated with the node.
    :param type: The type of connection.
    :param fromnode: The id of the origin node.
    :param tonode: The id of the destination node.
    :param metadata: Json formatted metadata associated with the connection.
    :return The id of the created connection.
    """
    return executeStatement(CREATE_CONNECTION, (projectId, type, fromnode, tonode, metadata), True)

@CanWrite
def deleteNode(nodeId=nodeId):
    """
    Helper to delete a node.
    :param nodeId: Id of the node to delete.
    """
    executeStatement(DELETE_NODE, (nodeId, nodeId), False)

@CanWrite
def deleteConnection(connectionId=connectionId):
    """
    Helper to delete a connection.
    :param connectionId: Id of the connection to delete.
    """
    executeStatement(DELETE_CONNECTION, (connectionId), False)

@CanWrite
def updateConnection(uid=userId,
                     pid=projectId,
                     connectionId=connectionId,
                     type=type,
                     fromNode=fromnode,
                     toNode=tonode,
                     metadata=metadata):
    executeStatement(UPDATE_CONNECTION, (type, tonode, fromnode, metadata, connectionId), False)

@CanWrite
def updateNode(uid=userId,
               pid=projectId,
               nodeId=nodeId,
               x=x,
               y=y,
               type=type,
               content=content):
    #updates all fields
    executeStatement(UPDATE_NODE, (x, y, type, content, nodeId),False)

def checkIfNodeIsInProject(uid=userId,
                           pid=projectId,
                           nodeId=nodeId):
    """returns a boolean if a node is in a project"""
    return executeStatement(CHECK_IF_NODE_IS_IN_PROJECT, (nodeId, projectId), True)

def checkIfConnectionIsInProject(uid=userId,
                                 pid=projectId,
                                 connectionId=connectionId):
    """returns a boolean if a connection is in a project"""
    return executeStatement(CHECK_IF_CONNECTION_IS_IN_PROJECT, (connectionId, projectId),True)

def checkPermissionsNode(uid=userId,
                         pid=projectId,
                         nodeId=nodeId):
    """checks if a node is in the project"""
    return checkIfNodeIsInProject(userId, projectId, nodeId)

def checkPermissionsConnection(uid=userId,
                               pid=projectId,
                               connectionId=connectionId):
    #checks the permissions for a conncetion
    return checkIfConnectionIsInProject(uid=userId, pid=projectId, connectionId=connectionId)

def checkIfUserIsInProject(uid=userId,
                           pid=projectId):
    return executeStatement(CHECK_IF_USER_IS_IN_PROJECT, (projectId, userId), True)

def verifyUserCanRead(uid=userId,
                      pid=projectId):
    #return boolean if the user can ready
    return checkIfUserIsInProject(userId, projectId)

def verifyUserCanEdit(uid=userId,
                      pid=projectId):
    #verify is a user has read permissions on a graph
    return checkIfUserIsInProject(userId, projectId)

#will create the tables if they don't exist
initTables()

