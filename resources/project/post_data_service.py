from resources.abstract_base_data_service import BaseDataService
import json


class PostDataService(BaseDataService):

    def __init__(self, config: dict):
        """

        :param config: A dictionary of configuration parameters.
        """
        super().__init__()

        self.data_dir = config['data_directory']
        self.data_file = config["data_file"]
        self.students = []

        self._load()

    def _get_data_file_name(self):
        # DFF TODO Using os.path is better than string concat
        result = self.data_dir + "/" + self.data_file
        return result

    def _load(self):

        fn = self._get_data_file_name()
        with open(fn, "r") as in_file:
            self.students = json.load(in_file)

    def _save(self):
        fn = self._get_data_file_name()
        with open(fn, "w") as out_file:
            json.dump(self.students, out_file)

    def get_posts(self, uni: str = None, first_name: str = None, last_name: str = None, school_code: str = None, post_id: str = None) -> list:
        """

        Returns students with properties matching the values. Only non-None parameters apply to
        the filtering.

        :param uni: UNI to match.
        param first_name: first_name to match.
        :param last_name: last_name to match.
        :param school_code: school_code to match.
        param post_id: post_id to match.
        :return: A list of matching JSON records.
        """
        result = []

        for s in self.students:

            if (uni is None or (s.get("uni", None) == uni)) and \
                    (first_name is None or (s.get("first_name", None) == first_name)) and \
                    (last_name is None or (s.get("last_name", None) == last_name)) and \
                    (school_code is None or (s.get("school_code", None) == school_code)) and \
                    (post_id is None or (s.get("post_id", None) == post_id)):
                    result.append(s)

        return result

