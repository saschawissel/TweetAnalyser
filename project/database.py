from psycopg2 import pool


class Database:
    __connection_pool = None  # static (since declared in class) and private (the 2 _ as prefix)

    @classmethod
    def initialize(cls, **kwargs):  # **kwargs: accept any number of named params
        cls.__connection_pool = pool.SimpleConnectionPool(1, 1, **kwargs)

    @classmethod
    def get_connection(cls):
        return cls.__connection_pool.getconn()

    @classmethod
    def return_connection(cls, connection):
        cls.__connection_pool.putconn(connection)

    @classmethod
    def close_all_connections(cls):
        cls.__connection_pool.closeall()


class CursorFromConnectionFromPool:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def __enter__(self):
        self.connection = Database.get_connection()
        self.cursor = self.connection.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is not None:
            self.connection.rollback()
        else:
            self.cursor.close()
            self.connection.commit()
        Database.return_connection(self.connection)

# Achtung: dieses Vorgehen ist ein "auto commit".
# Ein explizites Commit ist nur umsetzbar, wenn der Cursor im nutzenden Code explizit verwaltet wird.
