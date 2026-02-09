from fastapi import HTTPException

def api_error(status_code: int, error_code: str, message: str):
    # Consistent error shape for the whole backend
    raise HTTPException(
        status_code=status_code,
        detail={
            "error_code": error_code,
            "message": message,
        }
    )