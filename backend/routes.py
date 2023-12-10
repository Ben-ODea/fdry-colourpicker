from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel, constr

from functions import handle_form

app = FastAPI()

@app.get("/", include_in_schema=False)
async def get_index(): return FileResponse("frontend/index.html")

@app.get("/styles.css", include_in_schema=False)
async def get_styles(): return FileResponse("frontend/styles.css")

@app.get("/script.js", include_in_schema=False)
async def get_scripts(): return FileResponse("frontend/script.js")

@app.get("/favicon.ico", include_in_schema=False)
async def get_favicon(): return None # return FileResponse("frontend/favicon.ico") # TODO: favicon


class User(BaseModel):
    name: constr(min_length=1, max_length=100)
    workplace: constr(min_length=1, max_length=100)
    answer: constr(min_length=1, max_length=5000)
@app.post("/submit")
async def post_form(user: User): return handle_form(user.model_dump())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
