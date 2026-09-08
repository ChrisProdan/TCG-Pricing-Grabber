from __future__ import annotations

from backend.config import Settings

import psycopg

def get_connection(settings: Settings) -> psycopg.Connection:
    
    
    return psycopg.connect(dbname=settings.db_name,
                         user=settings.db_user,
                         password=settings.db_password,
                         port=settings.db_port,
                         host=settings.db_host,
                         autocommit=True)

def getSet(conn: psycopg.Connection, setName):
    with conn.cursor as cur:
        try:
            cur.execute(
                t"SELECT groupid FROM groupdata WHERE setname={setName}"
            )
            
            retval = cur.fetchone()
            if retval is None:
                return -1
            return retval[0]
            
        except psycopg.Error as e:
            return -1        

        