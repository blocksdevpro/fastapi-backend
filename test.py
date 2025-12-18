from app.handlers.response import response_handler
from app.handlers.exception import http_exception_handler, validation_exception_handler, rate_limit_exception_handler
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi import FastAPI
from fastapi.requests import Request


app = FastAPI()


@app.get("/")
@response_handler()
def read_root():
    raise Exception("value")


app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
