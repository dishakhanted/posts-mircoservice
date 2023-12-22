from resources.abstract_base_data_service import BaseDataService
from resources.database.database_data_service import DatabaseDataService
import json


class PostDataService(BaseDataService):

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

        posts = """CREATE TABLE IF NOT EXISTS "userPosts" (
        "userPostID" serial,
        "userID" int,
        "postID" int,
        "postContent" text,
        "dateOfCreation" timestamp,
        PRIMARY KEY ("userPostID"),
        CONSTRAINT "FK_userPosts.postID"
            FOREIGN KEY ("postID")
            REFERENCES "postThread"("postID"),
        CONSTRAINT "FK_userPosts.userID"
            FOREIGN KEY ("userID")
            REFERENCES "postUsers"("userID")
        );"""
        threads = """CREATE TABLE IF NOT EXISTS "postThread" (
        "postID" serial,
        "dateOfCreation" timestamp,
        PRIMARY KEY ("postID")
        );"""
        self.database.execute_query(threads)
        self.database.execute_query(posts)

    def get_database(self):
        return self.database

    def get_posts(self, userID: int, postThreadID: int, postID: int, postContent: int, offset: int, limit: int) -> list:
        """

        Returns students with properties matching the values. Only non-None parameters apply to
        the filtering.

        :param uni: UNI to match.
        :param last_name: last_name to match.
        :param school_code: first_name to match.
        :return: A list of matching JSON records.
        """
        result = []

        params = ["""\"userID\"""", """\"postID\"""", """\"userPostID\"""", """\"postContent\"""", """\"offset\"""", """\"limit\""""]
        values = [userID, postThreadID, postID, postContent, offset, limit]

        query = """SELECT * FROM \"userPosts\""""
        conditions = []
        for param, value in zip(params, values):
            if value is not None:
                if param == """\"postContent\"""":
                    conditions.append(f"{param} LIKE %s")
                else:
                    conditions.append(f"{param} = %s")
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += ";"
              
        posts = self.database.fetchallquery(query, tuple(value for value in values if value is not None))

        for s in posts:
            s['dateOfCreation'] = s['dateOfCreation'].strftime("%m/%d/%Y, %H:%M:%S")
            result.append(s)

        return result
    
    def add_post(self, request: dict) -> list:
        """

        Adds a post to a thread. Thread is created if the current ID doesnt exist.

        :param request: POST request with post data.
        """
        self.database.execute_query("INSERT INTO \"postThread\" (\"postID\", \"dateOfCreation\") VALUES (%s, CURRENT_TIMESTAMP) ON CONFLICT DO NOTHING", (request.postID,))
        posts = self.database.execute_query("INSERT INTO \"userPosts\" (\"userPostID\", \"userID\", \"postID\", \"postContent\", \"dateOfCreation\") VALUES (DEFAULT, %s, %s, %s, CURRENT_TIMESTAMP) RETURNING \"postID\"", (request.userID, request.postID, request.postContent))
        result = posts.fetchone()

        return result
    
    def put_post(self, request: dict) -> list:
        """

        Puts a post to a thread. Thread is created if the current ID doesnt exist.

        :param request: POST request with post data.
        """
        self.database.execute_query("INSERT INTO \"postThread\" (\"postID\", \"dateOfCreation\") VALUES (%s, CURRENT_TIMESTAMP) ON CONFLICT DO NOTHING", (request.postID,))
        posts = self.database.execute_query("INSERT INTO \"userPosts\" (\"userPostID\", \"userID\", \"postID\", \"postContent\", \"dateOfCreation\") VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP) ON CONFLICT (\"userPostID\") DO UPDATE SET \"postContent\"=%s, \"dateOfCreation\"=CURRENT_TIMESTAMP RETURNING \"postID\"", (request.userPostID, request.userID, request.postID, request.postContent, request.postContent))
        result = posts.fetchone()

        return result
    
    def delete_post(self, request: dict) -> list:
        """

        Deletes a post from a thread.

        :param request: DELETE request with post ID.
        """
        posts = self.database.execute_query("DELETE FROM \"userPosts\" WHERE \"userPostID\" = %s RETURNING \"postID\"", (request.userPostID,))
        result = posts.fetchone()

        return result

