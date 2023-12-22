from resources.abstract_base_resource import BaseResource
from resources.posts.post_models import PostRspModel, PostModel
from resources.rest_models import Link
from typing import List


class PostResource(BaseResource):
    #
    # This code is just to get us started.
    # It is also pretty sloppy code.
    #

    def __init__(self, config):
        super().__init__()

        self.data_service = config["data_service"]

    @staticmethod
    def _generate_links(s: dict) -> PostRspModel:
        self_link = Link(**{
            "rel": "self",
            "href": "/users/" + str(s['userID'])
        })

        links = [
            self_link,
        ]
        rsp = PostRspModel(**s, links=links)
        return rsp

    def get_posts(self, userID: int, postThreadID: int, postID: int, postContent: int, offset: int, limit: int) -> List[PostRspModel]:
        result = self.data_service.get_posts(userID, postThreadID, postID, postContent, offset, limit)
        final_result = []

        for s in result:
            p = self._generate_links(s)
            final_result.append(p)

        return final_result

    def add_post(self, request: PostModel) -> List[PostRspModel]:
        result = self.data_service.add_post(request)
        return result
    
    def put_post(self, request: PostModel) -> List[PostRspModel]:
        result = self.data_service.put_post(request)
        return result

    def delete_post(self, request: PostModel) -> List[PostRspModel]:
        result = self.data_service.delete_post(request)
        return result
