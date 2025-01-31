from resources.abstract_base_data_service import BaseDataService
from resources.database.database_data_service import DatabaseDataService
import json


class UserDataService(BaseDataService):

    def __init__(self, config: dict):
        """

        :param config: A dictionary of configuration parameters.
        """
        super().__init__()

        #self.data_dir = config['data_directory']
        #self.data_file = config["data_file"]
        #self.students = []

        self.database = DatabaseDataService(config)
        self._load()

    def _load(self):

        users = """CREATE TABLE IF NOT EXISTS "postUsers" (
        "userID" serial,
        "firstName" text,
        "lastName" text,
        "isAdmin" boolean,
        PRIMARY KEY ("userID")
        );"""
        
        self.database.execute_query(users)


    def _save(self):
        fn = self._get_data_file_name()
        with open(fn, "w") as out_file:
            json.dump(self.students, out_file)

    def get_database(self):
        return self.database

    def get_users(self, userID: int, firstName: str, lastName: str, isAdmin: bool, offset: int, limit: int) -> list:
        """

        Returns users with properties matching the values. Only non-None parameters apply to
        the filtering.

        :param userID: userID to match.
        :return: A list of matching JSON records.
        """
        result = []
        users = {}
        # Define a list of parameters and their values
        params = ["""\"userID\"""", """\"firstName\"""", """\"lastName\"""", """\"isAdmin\"""", """\"offset\"""", """\"limit\""""]
        values = [userID, firstName, lastName, isAdmin, offset, limit]

        query = """SELECT * FROM "postUsers" """
        conditions = []
        for param, value in zip(params, values):
            if value is not None:
                conditions.append(f"{param} = %s")
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += ";"

        
        users = self.database.fetchallquery(query, tuple(value for value in values if value is not None))
        for s in users:
            result.append(s)

        return result
    
    def add_user(self, request: dict) -> list:
        """
    
        Adds students with properties matching the values. Only non-None parameters apply to
        the filtering.

        :param request: A dictionary of the UserModel
        :return: userID of the newly created user.
        """
    
        users = self.database.execute_query("""INSERT INTO \"postUsers\" (\"userID\", \"firstName\", \"lastName\", \"isAdmin\") VALUES (DEFAULT, %s, %s, %s) RETURNING \"userID\"""", (request.firstName, request.lastName, request.isAdmin))
        result = users.fetchone()

        return result
        
    def delete_user(self, request: dict) -> list:
        """

        Deletes a message from a thread.

        :param request: DELETE request with message ID.
        """
        users = self.database.execute_query("DELETE FROM \"postUsers\" WHERE \"userID\" = %s RETURNING \"userID\"", (request.userID,))
        result = users.fetchone()

        return result
