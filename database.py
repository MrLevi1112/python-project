import mysql.connector
from mysql.connector import Error

def create_connection(host_name, user_name, user_password, db_name):
    """
    Create a connection to a MySQL database.
    """
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            password=user_password,
            database=db_name
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection

def execute_query(connection, query):
    """
    Execute a query that modifies the database.
    """
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")

def execute_read_query(connection, query):
    """
    Execute a query that reads from the database.
    """
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")
        return result

if __name__ == '__main__':
    # Update these parameters with your actual MySQL server credentials and database name.
    connection = create_connection("localhost", "root", "IdodoBird!1", "tic_tac_toe_db")
    create_table_query = """
    CREATE TABLE IF NOT EXISTS game_results (
        game_id INT AUTO_INCREMENT,
        player1 VARCHAR(100) NOT NULL,
        player2 VARCHAR(100) NOT NULL,
        winner VARCHAR(100) NOT NULL,
        mode VARCHAR(10) NOT NULL,
        game_date DATE NOT NULL,
        game_time TIME NOT NULL,
        PRIMARY KEY (game_id)
    ) ENGINE = InnoDB;
    """
    if connection:
        execute_query(connection, create_table_query)
