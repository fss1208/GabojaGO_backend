from datetime import datetime, timedelta
import pandas as pd
import pymysql
import logging
import os

logger = logging.getLogger(__name__)

class DatabaseException(Exception):

    def __init__(self, strMessage):
        self.m_strMessage = strMessage

    def __str__(self):
        return self.m_strMessage
    
    @property
    def Message(self):
        return self.m_strMessage

class DATABASE:

    TUPLE_SYMBOL = "%s" # MySQL
    CHARSET = "utf8"

    @staticmethod
    def CONNECT(name: str = None):
        try:
            dt = datetime.now()
            name = name if name else os.getenv("DBNAME")
            connection = pymysql.connect(
                host=os.getenv("DBHOST"), 
                port=int(os.getenv("DBPORT")),
                user=os.getenv("DBUSER"), 
                passwd=os.getenv("DBPSWD"),
                charset=DATABASE.CHARSET
            )
            logger.info("DATABASE 연결 성공 ({}:{}, {:,.2f}msec)".format(connection.host, connection.port, (datetime.now() - dt).microseconds/1000))
            if name:
                connection.select_db(name)
            return connection
        except Exception as e:
            logger.error("DATABASE 연결 실패 ({}:{})".format(os.getenv("DBHOST"), os.getenv("DBPORT")))
            raise DatabaseException(str(e))

    @staticmethod
    def EXECUTE(cursor, query: str):
        try:
            dt = datetime.now()
            result = cursor.execute(query)
            logger.debug("[SQL] {} >> result={}, msec={:,.2f}".format(query, result, (datetime.now() - dt).microseconds/1000))
            return result
        except Exception as e:
            logger.error("[{}] {}".format(type(e), e))
            raise DatabaseException(str(e))

    @staticmethod
    def EXECUTE1(cursor, query: str, value: tuple):
        try:
            dt = datetime.now()
            result = cursor.execute(query, value)
            logger.debug("[SQL] {} >> result={}, msec={:,.2f}".format(query, result, (datetime.now() - dt).microseconds/1000))
            return result
        except Exception as e:
            logger.error("[{}] {}".format(type(e), e))
            raise DatabaseException(str(e))

    @staticmethod
    def EXECUTES(cursor, query: str, values: tuple):
        try:
            dt = datetime.now()
            result = cursor.executemany(query, values)
            logger.debug("[SQL] {} >> result={}, msec={:,.2f}".format(query, result, (datetime.now() - dt).microseconds/1000))
            return result
        except Exception as e:
            logger.error("[{}] {}".format(type(e), e))
            raise DatabaseException(str(e))

    @staticmethod
    def SELECT(connection, query: str):
        try:
            dt = datetime.now()
            df = pd.read_sql(query, connection)
            logger.debug("[SQL] {} >> result={}, msec={:,.2f}".format(query, df.shape[0], (datetime.now() - dt).microseconds/1000))
            return df
        except Exception as e:
            logger.error("[{}] {}".format(type(e), e))
            raise DatabaseException(str(e))
