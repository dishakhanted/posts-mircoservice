# FastAPI is a framework and library for implementing REST web services in Python.
# https://fastapi.tiangolo.com/
#
from fastapi import FastAPI, RedirectResponse, HTTPException
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


def get_data_service():
    database = {}
    if LOCAL:
        database = {
            "db_name": "post",
            "db_host": "localhost",
            "db_user": "post",
            "db_pass": "post",
        }
    else:
        database = {
            "db_name": "post",
            "db_host": '/cloudsql/{}'.format("ecbm4040-vc2652:us-east1:post-db"),
            "db_user": "post",
            "db_pass": "post",
        }

    ds = UserDataService(database)
    return ds


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
            "db_pass": "post",
        }
    else:
        database = {
            "db_name": "post",
            "db_host": '/cloudsql/{}'.format("ecbm4040-vc2652:us-east1:post-db"),
            "db_user": "post",
            "db_pass": "post",
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
async def profile(request: HTMLResponse, userID: int):
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


@app.get("/api/posts", response_model=List[PostRspModel])
async def get_posts(userID: int | None = None, postID: int | None = None, postContent: int | None = None,
                    offset: int | None = None, limit: int | None = None):
    """
    Returns all posts.
    """
    result = post_resource.get_posts(userID, postID, postContent, offset, limit)
    return result


@app.post("/api/posts/newPost")
def new_post(request: PostModel):
    result = post_resource.add_post(request)
    if len(result) == 1:
        result = result[0]
    else:
        raise HTTPException(status_code=404, detail="Not found")

    return result


@app.put("/api/posts/newPost")
def new_message(request: PostModel):
    result = post_resource.put_post(request)
    if len(result) == 1:
        result = result[0]
    else:
        raise HTTPException(status_code=404, detail="Not found")

    return result


@app.delete("/api/posts/newPost")
def new_post(request: PostModel):
    result = post_resource.delete_post(request)
    if len(result) == 1:
        result = result[0]
    else:
        raise HTTPException(status_code=404, detail="Not found")

    return result


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8012, reload=True)
