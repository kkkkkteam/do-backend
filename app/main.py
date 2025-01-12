from fastapi import FastAPI
from api.common import api_v1_router as common_api_v1_router
from api.admin import api_v1_router as admin_api_v1_router
from api.user import api_v1_router as user_api_v1_router
from db.session import SessionLocal, engine
from db.models import user_model

import uvicorn

user_model.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(common_api_v1_router)
app.include_router(admin_api_v1_router)
#app.include_router(user_api_v1_router)

if __name__ == "__main__":
    # For Production Build
    # uvicorn.run("main:app", host="0.0.0.0", port=8000)

    # For Development Build
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

