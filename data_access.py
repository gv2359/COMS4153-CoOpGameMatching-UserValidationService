from abc import ABC, abstractmethod, abstractclassmethod
import pymysql

class DataService(ABC):
    """
    Abstract base class for data service that defines the interface of concrete
    data service classes. This approach allows writing application logic that is
    independent from specific database choices.
    """

    def __init__(self, context):
        """
        This is a simple approach to dependency injection. The context will contain references
        to configuration information that an instance needs.
        :param context:
        """
        self.context = context

    @abstractmethod
    def _get_connection(self):
        """
        Create and return a connection to the database instance for this data services.
        :return: A connection.
        """
        raise NotImplementedError('Abstract method _get_connection()')
    
    @abstractmethod
    def get_data_object(self,
                        database_name: str,
                        collection_name: str,
                        key_field: str,
                        key_value: str):
        """
        Gets a single data object from a table in a database. Collection is an abstraction of a
        table in the relational model, collection in MongoDB, etc.

        :param database_name: Name of the database or similar abstraction.
        :param collection_name: The name of the collection, table, etc. in the database.
        :param key_field: A single column, field, ... that is a unique key/identifier.
        :param key_value: The value for the column, field, ... ...
        :return: The single object identified by the unique field.
        """
        raise NotImplementedError('Abstract method get_data_object()')
    
    @abstractmethod
    def insert_data_object(self,
                           database_name: str,
                           collection_name: str,
                           data_object: dict):
        """
        Insert a new data object into a specified database and collection.

        :param database_name: Name of the database to insert into.
        :param collection_name: Name of the table to insert into.
        :param data_object: Dictionary representing the data object to insert.
        :return: True if insertion was successful, False otherwise.
        """
        raise NotImplementedError('Abstract method insert_data_object()')


class MySQLDataService(DataService):
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

    def get_data_object(self,
                        database_name: str,
                        collection_name: str,
                        key_field: str,
                        key_value: str):
        """
        See base class for comments.
        """

        connection = None
        result = None
        try:
            sql_statement = f"SELECT * FROM {database_name}.{collection_name} " + \
                        f"where {key_field}=%s"
            connection = self._get_connection()
            cursor = connection.cursor()
            cursor.execute(sql_statement, [key_value])
            result = cursor.fetchone()
        except Exception as e:
            if connection:
                connection.close()

        return result

    def insert_data_object(self,
                           database_name: str,
                           collection_name: str,
                           data_object: dict):
        """
        See base class for comments.
        """
        connection = None
        success = False

        try:
            # Prepare the SQL statement
            columns = ', '.join(data_object.keys())
            placeholders = ', '.join(['%s'] * len(data_object))
            sql_statement = f"INSERT INTO {database_name}.{collection_name} ({columns}) VALUES ({placeholders})"

            connection = self._get_connection()
            cursor = connection.cursor()

            # Execute the insertion
            cursor.execute(sql_statement, tuple(data_object.values()))
            connection.commit()  # Commit the transaction
            success = True  # Set success to True if no exceptions were raised
        except Exception as e:
            print(f"Error while inserting data: {e}")
        finally:
            if connection:
                connection.close()  # Ensure the connection is closed

        return success