from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.logger import get_logger
from app.exceptions import AppError

log = get_logger(__name__)

class ExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except AppError as e:
            log.warning(f"Handled AppError: {e}", exc_info=True)
            return JSONResponse(
                status_code=400,
                content={"error": str(e), "type": e.__class__.__name__}
            )
        except Exception as e:
            log.error(f"Unhandled exception: {e}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={"error": "Internal Server Error", "type": "UnhandledException"}
            )
