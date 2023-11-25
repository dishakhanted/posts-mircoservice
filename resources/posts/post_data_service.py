from resources.abstract_base_data_service import BaseDataService
from resources.database.database_data_service import DatabaseDataService
import json
from resources.posts.post_models import PostModel


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

    #def _get_data_file_name(self):
        # DFF TODO Using os.path is better than string concat
        #result = self.data_dir + "/" + self.data_file
       #return result

    def _load(self):

        posts = """CREATE TABLE IF NOT EXISTS "userPosts" (
        "userPostID" serial,
        "userID" int,
        "postID" int,
        "postContent" text,
        "dateOfCreation" timestamp,
        PRIMARY KEY ("userPostsID"),
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

    def get_posts(self, userID: int, postID: int, postContent: int, offset: int, limit: int) -> list:
        result = []
        posts = {}
        query = """SELECT * FROM "userPosts" """
        if (userID is None and postID is None and postContent is None and offset is None and limit is None):
            query += """;"""
        else:
            query += """ WHERE 1=1"""
            if (userID is not None):
                query += """ AND "userID"=""" + str(userID)
            if (postID is not None):
                query += """ AND "postID"='""" + str(postID) + """'"""
            if (postContent is not None):
                query += """ AND "postContent" LIKE '%""" + str(postContent) + """%'"""
            if (limit is not None):
                if (offset is not None):
                    query += """ LIMIT """ + str(limit) + """ OFFSET """ + str(offset)
                else:
                    query += """ LIMIT """ + str(limit)
            query += """;"""

        posts = self.database.fetchallquery(query)
        for s in posts:
            s['dateOfCreation'] = s['dateOfCreation'].strftime("%m/%d/%Y, %H:%M:%S")
            result.append(s)

        return result
    
    def add_post(self, request: dict) -> list:
        check_thread = f"""INSERT INTO "postThread" ("postID", "dateOfCreation") VALUES ('{request.postID}', CURRENT_TIMESTAMP) ON CONFLICT DO NOTHING"""
        self.database.execute_query(check_thread)
        query = f"""INSERT INTO "userPosts"("userPostID", "userID", "postID", "postContent", "dateOfCreation") VALUES (DEFAULT, '{request.userID}', '{request.postID}' , '{request.postContent}', CURRENT_TIMESTAMP) RETURNING "postID";"""
        posts = self.database.execute_query(query)
        result = posts.fetchone()

        return result

    def put_post(self, request: dict) -> list:
        check_thread = f"""INSERT INTO "postThread" ("postID", "dateOfCreation") VALUES ('{request.postID}', CURRENT_TIMESTAMP) ON CONFLICT DO NOTHING"""
        self.database.execute_query(check_thread)
        query = f"""INSERT INTO "userPosts"("userPostID", "userID", "postID", "postContent", "dateOfCreation") VALUES ('{request.userPostID}', '{request.userID}', '{request.postID}' , '{request.postContent}', CURRENT_TIMESTAMP) ON CONFLICT ("userPostID") DO UPDATE SET "postContent"='{request.postContent}', "dateOfCreation"=CURRENT_TIMESTAMP RETURNING "postID";"""
        posts = self.database.execute_query(query)
        result = posts.fetchone()

        return result

    def delete_post(self, request: dict) -> list:
        query = f"""DELETE FROM "userPosts" WHERE "userPostID" = '{request.userPostID}' RETURNING "postID";"""
        posts = self.database.execute_query(query)
        result = posts.fetchone()

        return result

