import pymysql
from framework.services.DataAccess.BaseDataService import BaseDataService


class MySQLDataService(BaseDataService):
    """
    A generic data service for MySQL databases. The class implement common
    methods from BaseDataService and other methods for MySQL. More complex use cases
    can subclass, reuse methods and extend.
    """

    def __init__(self, context):
        super().__init__(context)

    def _get_connection(self):
        connection = pymysql.connect(
            host=self.context["host"],
            port=self.context["port"],
            user=self.context["user"],
            passwd=self.context["password"],
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True
        )
        return connection

    def get_data_object(self, database_name, collection_name, key_field, key_value):
        """Fetch a single record based on a unique key field."""
        sql_statement = f"SELECT * FROM {database_name}.{collection_name} WHERE {key_field} = %s"
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql_statement, (key_value,))
                return cursor.fetchone()

    def get_all_data_objects(self, database_name, collection_name, offset, limit):
        """Fetch all records from a specified table with pagination."""
        sql_statement = f"SELECT * FROM {database_name}.{collection_name} LIMIT %s OFFSET %s"
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql_statement, (limit, offset))
                return cursor.fetchall()

    def execute_query(self, query, params):
        """Execute a given SQL query with parameters and return the results."""
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()

    def insert_data_object(self, database_name, collection_name, data_object):
        """Insert a new record into a specified table."""
        columns = ', '.join(data_object.keys())
        placeholders = ', '.join(['%s'] * len(data_object))
        sql_statement = f"INSERT INTO {database_name}.{collection_name} ({columns}) VALUES ({placeholders})"
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql_statement, tuple(data_object.values()))
                connection.commit()
                return cursor.rowcount > 0  # Returns True if the insertion was successful

    def update_data_object(self, database_name, collection_name, key_field, key_value, updated_data):
        """Update an existing record in a specified table based on a unique key field."""
        set_clause = ', '.join([f"{key} = %s" for key in updated_data.keys()])
        sql_statement = f"UPDATE {database_name}.{collection_name} SET {set_clause} WHERE {key_field} = %s"

        # Prepare the parameters for the query
        params = tuple(updated_data.values()) + (key_value,)

        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql_statement, params)
                connection.commit()
                return cursor.rowcount > 0