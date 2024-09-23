import pandas as pd
import numpy as np

import sqlite3
import json

import sqlite3


class DatabaseManager:
    def __init__(self, db_name):
        """
        Initializes the DatabaseManager with the specified database name.

        Parameters:
        - db_name: str. The name or path of the SQLite3 database file to connect to.
        """
        self.db_name = db_name
        self.connection = None
        self.cursor = None

    def connect(self):
        """
        Establishes a connection to the SQLite3 database and creates a cursor.
        """
        try:
            self.connection = sqlite3.connect(self.db_name)
            self.cursor = self.connection.cursor()
            print(f"Connected to {self.db_name}")
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")

    def create_table(self, table_query):
        """
        Executes a SQL query to create a table in the database.

        Parameters:
        - table_query: str. SQL query to create the table.
        """
        try:
            self.cursor.execute(table_query)
            self.connection.commit()
            print("Table created successfully.")
        except sqlite3.Error as e:
            print(f"Error creating table: {e}")

    def insert_data(self, insert_query, data):
        """
        Inserts data into a table.

        Parameters:
        - insert_query: str. SQL query for inserting data.
        - data: tuple. The data to insert into the table.
        """
        try:
            self.cursor.execute(insert_query, data)
            self.connection.commit()
            print("Data inserted successfully.")
        except sqlite3.Error as e:
            print(f"Error inserting data: {e}")

    def fetch_data(self, select_query):
        """
        Fetches data from the database based on a SELECT query.

        Parameters:
        - select_query: str. SQL query to fetch data.

        Returns:
        - list of tuples. The fetched data from the query.
        """
        try:
            temp_df = pd.read_sql(select_query, self.connection)
            #self.cursor.execute(select_query)
            #result = self.cursor.fetchall()
            return temp_df
        except sqlite3.Error as e:
            print(f"Error fetching data: {e}")
            return None

    def close(self):
        """
        Closes the connection to the SQLite3 database.
        """
        if self.connection:
            self.connection.close()
            print(f"Connection to {self.db_name} closed.")

# Example usage:
# db = DatabaseManager('my_database.db')
# db.connect()
# db.create_table("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)")
# db.insert_data("INSERT INTO users (name, age) VALUES (?, ?)", ("John Doe", 25))
# data = db.fetch_data("SELECT * FROM users")
# print(data)
# db.close()