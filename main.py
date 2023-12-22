# FastAPI is a framework and library for implementing REST web services in Python.
# https://fastapi.tiangolo.com/

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List, Union
from google.cloud import pubsub_v1
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from typing import List, Union
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Depends

# I like to launch directly and not use the standard FastAPI startup process.
# So, I include uvicorn
import uvicorn

from resources.posts.post_data_service import PostDataService
from resources.posts.post_resource import PostRspModel, PostModel, PostResource
from resources.users.users_data_service import UserDataService
from resources.users.users_resource import UserResource
from resources.users.users_models import UserRspModel, UserModel

LOCAL = False

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
# Google Cloud Pub/Sub settings
PROJECT_ID = "ecbm4040-spr2139"
TOPIC_NAME_USER = "user_created"
TOPIC_NAME_POST = "posts_created"

# Create Pub/Sub publisher clients
publisher_user = pubsub_v1.PublisherClient()
topic_user_path = publisher_user.topic_path(PROJECT_ID, TOPIC_NAME_USER)

publisher_post = pubsub_v1.PublisherClient()
topic_post_path = publisher_post.topic_path(PROJECT_ID, TOPIC_NAME_POST)


def get_data_service():
    database = {}
    if LOCAL:
        database = {
            "db_name": "post",
            "db_host": "localhost",
            "db_user": "post",
            "db_pass": "123456",
        }
    else:
        database = {
            "db_name": "post",
            "db_host": '/cloudsql/{}'.format("ecbm4040-spr2139:us-east1:post-db"),
            "db_user": "post",
            "db_pass": "123456",
        }

    ds = UserDataService(database)
    return ds

def publish_message(topic_path, data):
    data = data.encode("utf-8")
    future = publisher_user.publish(topic_path, data)
    future.result()


def get_user_resource():
    ds = get_data_service()
    config = {
        "data_service": ds
    }
    res = UserResource(config)
    return res


user_resource = get_user_resource()


def get_post_resource():
    database = {}
    if LOCAL:
        database = {
            "db_name": "post",
            "db_host": "localhost",
            "db_user": "post",
            "db_pass": "123456",
        }
    else:
        database = {
            "db_name": "post",
            "db_host": '/cloudsql/{}'.format("ecbm4040-spr2139:us-east1:post-db"),
            "db_user": "post",
            "db_pass": "123456",
        }

    ds = PostDataService(database)

    config = {
        "data_service": ds
    }
    res = PostResource(config)
    return res


post_resource = get_post_resource()


@app.get("/")
async def root():
    return RedirectResponse("/static/index.html")


@app.get("/api")
async def api():
    """
    Redirects to FastAPI Documentation.
    """
    return RedirectResponse("/docs")


@app.get("/profile/{userID}", response_class=HTMLResponse)
async def profile(request: Request, userID: int):
    result = user_resource.get_users(userID, firstName=None, lastName=None, isAdmin=None, offset=None, limit=None)
    if len(result) == 1:
        result = result[0]
    else:
        raise HTTPException(status_code=404, detail="Not found")
    
    return templates.TemplateResponse("profile.html", {"request": request, "userID": userID, "result": result})


@app.get("/api/users", response_model=List[UserRspModel])
async def get_users(userID: int | None = None, firstName: str | None = None, lastName: str | None = None, isAdmin: bool | None = None,
                    offset: int | None = None, limit: int | None = None):
    """
    Return all users.
    """
    result = user_resource.get_users(userID, firstName, lastName, isAdmin, offset, limit)
    return result


@app.get("/api/users/{userID}", response_model=Union[List[UserRspModel], UserRspModel, None])
async def get_student(userID: int):
    """
    Return a user based on userID.

    - **userID**: User's userID
    """
    result = user_resource.get_users(userID, firstName=None, lastName=None, isAdmin=None, offset=None, limit=None)
    if len(result) == 1:
        result = result[0]
    else:
        raise HTTPException(status_code=404, detail="Not found")

    return result


@app.post("/api/users/newUser")
def add_users(request: UserModel):
    result = user_resource.add_user(request)
    if len(result) == 1:
        result = result[0]
    else:
        raise HTTPException(status_code=404, detail="Not found")

    return result

@app.post("/api/users/newUser", response_model=UserRspModel)
async def add_users(request: UserModel, background_tasks: BackgroundTasks):
    result = user_resource.add_user(request)
    if len(result) == 1:
        result = result[0]
    else:
        raise HTTPException(status_code=404, detail="Not found")
    # Publish a message when a new user is created
    message = f"User created: {result}"
    background_tasks.add_task(publish_message, topic_user_path, message)

    return result

@app.get("/api/posts", response_model=List[PostRspModel])
async def get_posts(userID: int | None = None, postThreadID: int | None = None,postID: int | None = None, postContent: int | None = None,
                    offset: int | None = None, limit: int | None = None):
    """
    Returns all posts.
    """
    result = post_resource.get_posts(userID, postThreadID, postID, postContent, offset, limit)
    return result

@app.get("/api/posts/{userID}", response_model=Union[List[PostRspModel], PostRspModel, None])
async def get_posts(userID: int):
    """
    Return messages based on userID.

    - **userID**: User's userID
    """
    
    result = post_resource.get_posts(userID,  postThreadID=None, postID=None, postContent=None, offset=None, limit=None)

    return result



@app.post("/api/posts/newPost")
def new_post(request: PostModel):
    
    result = None
    result = post_resource.add_post(request)
    if len(result) == 1:
        result = result[0]
    else:
        raise HTTPException(status_code=404, detail="Not found")
    
    return result

@app.post("/api/posts/newPost", response_model=PostRspModel)
async def new_post(request: PostModel, background_tasks: BackgroundTasks):
    result = post_resource.add_post(request)

    # Publish a message when a new post is created
    message = f"Post created: {result}"
    background_tasks.add_task(publish_message, topic_post_path, message)

    return result

@app.put("/api/posts/newPost")
def put_post(request: PostModel):
    
    result = None
    result = post_resource.put_post(request)
    if len(result) == 1:
        result = result[0]
    else:
        raise HTTPException(status_code=404, detail="Not found")
    
    return result

@app.delete("/api/posts/newPost")
def delete_post(request: PostModel):
    
    result = None
    result = post_resource.delete_post(request)
    if len(result) == 1:
        result = result[0]
    else:
        raise HTTPException(status_code=404, detail="Not found")
    
    return result

@app.delete("/api/users/deleteUser")
def delete_users(request: UserModel):
    
    result = user_resource.delete_user(request)
    if len(result) == 1:
        result = result[0]
    else:
        raise HTTPException(status_code=404, detail="Not found")
    
    return result

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8012, reload=True)
