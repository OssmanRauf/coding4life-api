from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import models
import db.database as database
import routers.comments as comments
import routers.posts as posts
import routers.users as users
import routers.oauth as oauth
import routers.admin as admin

# Connect models
models.Base.metadata.create_all(bind=database.engine)

# Init app object
app = FastAPI()


# resolving all cors object
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def main():
    return {"message": "Hello World"}


# Include routers into the main app
app.include_router(posts.router)
app.include_router(users.router)
app.include_router(oauth.router)
app.include_router(comments.router)
app.include_router(admin.router)
