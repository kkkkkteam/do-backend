from fastapi import APIRouter
from api.admin import admin, auth, department, job_group, user

api_v1_router = APIRouter(prefix="/api/v1")

# admin
api_v1_router.include_router(admin.router, tags=["admin"], prefix="/admin")
api_v1_router.include_router(user.router, tags=["admin/user"], prefix="/admin/user")
api_v1_router.include_router(auth.router, tags=["admin/auth"], prefix="/admin/auth")
api_v1_router.include_router(job_group.router, tags=["admin/job_group"], prefix="/admin/job_group")
api_v1_router.include_router(department.router, tags=["admin/department"], prefix="/admin/department")


