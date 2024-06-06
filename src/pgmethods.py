import psycopg2
import requests


class PgSQLMethods:
    """"""

    def __init__(
        self, user: str, secret: str, hostname: str, port: int, database: str
    ) -> None:
        """
        Initialize a new DatabaseConnection object with the provided connection details.

        Args:
            user (str): The username for the database connection.
            secret (str): The password or secret key for the database connection.
            hostname (str): The hostname or IP address of the database server.
            port (int | str): The port number for the database connection.
            database (str): The name of the database to connect to.

        Returns:
            None
        """
        self.swich = 0
        self.pg_user = user
        self.pg_secret = secret
        self.pg_hostname = hostname.split(",")
        self.pg_port = str(port).split(",")
        self.pg_database = database
        if not isinstance(self.pg_hostname, list):
            self.pg_hostname = [self.pg_hostname]
        if not isinstance(self.pg_port, list):
            self.pg_port = [self.pg_port]

    def health_check(self):
        try:
            conn = psycopg2.connect(
                user=self.pg_user,
                password=self.pg_secret,
                host=self.pg_hostname[self.swich],
                port=self.pg_port[self.swich],
                database=self.pg_database,
            )
            conn.close()
            return True
        except:
            return False
        
    def e__health_check(self):
        try:
            conn = psycopg2.connect(
                user=self.pg_user,
                password=self.pg_secret,
                host=self.pg_hostname[self.swich],
                port=self.pg_port[self.swich],
                database=self.pg_database,
            )
            conn.close()
            return True
        except Exception as e:
            return e
        
    def is_replica(self):
        return self.__execute_query("select pg_is_in_recovery();",psycopg2.cursor.fetchall)

    def __execute_query(self, query: str, results_retrieval) -> list:
        """
        Executes a SQL query against the database and returns the result.

        Args:
            query (str): The SQL query to execute.
            results_retrieval (Callable): A function that retrieves the results of the query. Defaults to None.
        Returns:
            output (list): The result of the query as a list. If `results_retrieval` is None, an empty list is returned.
        """
        try:
            with psycopg2.connect(
                user=self.pg_user,
                password=self.pg_secret,
                host=self.pg_hostname[self.swich],
                port=self.pg_port[self.swich],
                database=self.pg_database,
            ) as conn:
                with conn.cursor() as curr:
                    curr.execute(query)
                    if results_retrieval:
                        output = curr.results_retrieval()
                    else:
                        conn.commit()
                    curr.close()
                conn.close()
            if output:
                return output
        except:
            self.swich += 1
            with psycopg2.connect(
                user=self.pg_user,
                password=self.pg_secret,
                host=self.pg_hostname[self.swich],
                port=self.pg_port[self.swich],
                database=self.pg_database,
            ) as conn:
                with conn.cursor() as curr:
                    curr.execute(query)
                    if results_retrieval:
                        output = curr.results_retrieval()
                    else:
                        conn.commit()
                    curr.close()
                conn.close()
            if output:
                return output

    def create_table(self, table_name: str = "test", context: str = "(id int)") -> None:
        """
        Creates a new table in the database.

        Args:
            table_name (str): The name of the table to create. Defaults to "test".
            context (str): A string defining the column definitions for the table. Defaults to "(id int)".

        Returns:
            None
        """
        self.__execute_query("DROP TABLE [ IF EXISTS ] {}; CREATE TABLE {}{};".format(table_name,table_name,context))

    def insert(
        self, table_name: str = "test", columns: str = "id", values: str = "0"
    ) -> None:
        """
        Inserts data into a table.

        Args:
            table_name (str): The name of the table to insert data into. Defaults to "test".
            columns (str): A string defining the column names for the data. Defaults to "id".
            values (str): A string representing the values to be inserted. Defaults to 0.

        Returns:
            None
        """
        self.__execute_query("INSERT INTO {} ({}) VALUES ({});".format(table_name,columns,values))

    def select(self, table_name: str = "test", columns: str = "id") -> list:
        """
        Select data from a table.

        Args:
            table_name (str): The name of the table to insert data into. Defaults to "test".
            columns (str): A string defining the column names for the data. Defaults to "id".

        Returns:
            output (list): The result of the select query as a list of tuples.
        """
        return self.__execute_query(
            "SELECT {columns} FROM {};".format(columns,table_name), psycopg2.cursor.fetchall
        )
    
    def bench(self, counter):
        self.create_table()
        for i in range(int(counter)):
            self.insert(values=str(i))
        return len(self.select())
