"""
covid cast rest wrapper
"""
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    """
    main api endpoint
    """
    return {"message": "Hello World"}
