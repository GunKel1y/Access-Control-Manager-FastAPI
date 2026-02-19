from fastapi import APIRouter
from api.v1 import users, resources, accesses

router = APIRouter()

router.include_router(users.router)
router.include_router(resources.router)
router.include_router(accesses.router)