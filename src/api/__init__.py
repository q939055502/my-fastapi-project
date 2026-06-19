
"""
API Router Package
"""
from fastapi import APIRouterfrom src.api.v1 import v1_routerapi_router = APIRouter()


@api_router.get("/health")
async def health_check():
    """�������ӿ�"""
    return {"status": "healthy", "message": "Service is running"}


# Include v1 router
api_router.include_router(v1_router, prefix="/v1")

