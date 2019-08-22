# -*- coding: utf-8 -*-
"""
Created on Fri Jan 26 13:31:54 2018
@author: durandt
Database connection and execution module
"""

import logging 
import sqlalchemy 
import pyodbc

"""
Function to create the SQL Alchemy DB engine
"""
def create_engine(UID, PWD, DATABASE, SERVER, DRIVER):
    try:
        engine = sqlalchemy.create_engine("mssql+pyodbc://" + UID + ":" + PWD + "@" + SERVER + "/" + DATABASE + "?" + "driver=" + DRIVER + "")
        return engine
    except Exception as e:
        logging.exception("Exception")
        
"""
Function to create the SQL Alchemy DB engine using DSN
"""
def create_engine_DSN(UID, PWD, DSN, DATABASE):
    try:
        engine = sqlalchemy.create_engine("mssql+pyodbc://" + UID + ":" + PWD + "@" + DSN + "")
        engine.execute("USE " + DATABASE)
        return engine
    except Exception as e:
        logging.exception("Exception")
        
"""
Function to create the pyodbc connection
"""
def create_conn(UID, PWD, DSN, APP, DATABASE):
    try:
        conn = pyodbc.connect(
            r'DSN=' + DSN + ';'
            r'UID=' + UID + ';'
            r'PWD=' + PWD + ';'
            r'APP=' + APP + ';'
            r'DATABASE=' + DATABASE + ';'
            )
        return conn
    except Exception as e:
        logging.exception("Exception")  

"""
Function to write a dataframe to the database
"""
def write_df_db(engine, df, sourcetablename):
   try:
       logging.info("Started writing results to " + sourcetablename + "_TEMP")
       df.to_sql(sourcetablename + "_TEMP", engine, if_exists ="replace", index = False, chunksize = 20000)
       logging.info("Results written to " + sourcetablename + "_TEMP")
       return(df)
   except Exception as e:
        logging.exception("Exception")
        
"""
Call a stored procedure
"""
def call_proc(engine, procname, *args):
    try:
        logging.info("Executing proc: " + procname)
        conn = engine.raw_connection()
        with conn.cursor() as cursor:
            param_subs = sub_params([*args])
            params = [*args]
            sql = "exec [dbo].[" + procname + "] " + param_subs
            cursor.execute(sql, (params))
    except Exception as e:
        logging.exception("Exception")    















 

"""
Substitute the params for ? to run the stored procedure with a variable number of args
"""        
def sub_params(params): 
    try:
        return ",".join(["?" for arg in params])
    except Exception as e:
        logging.exception("Exception")  
        
        """
Combine params to run the stored procedure with a variable number of args
"""        
def combine_params(params): 
    try:
        return ",".join([arg for arg in params])
    except Exception as e:
        logging.exception("Exception")  
