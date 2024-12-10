import json
import os
from typing import Dict, List, Optional

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, File, UploadFile, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from backend.server.websocket_manager import WebSocketManager
from backend.server.server_utils import (
    get_config_dict,
    update_environment_variables, handle_file_upload, handle_file_deletion,
    execute_multi_agents, handle_websocket_communication,
    handle_research_data,
    handle_fetch_search_queries,
    handle_write_final_report,
    handle_fetch_final_report_download_url,
    handle_research_query
)
import asyncio
from contextlib import asynccontextmanager
from fastapi_utilities import repeat_at

# Models


class ResearchRequest(BaseModel):
    task: str
    report_type: str
    agent: str


class ConfigRequest(BaseModel):
    ANTHROPIC_API_KEY: str
    TAVILY_API_KEY: str
    LANGCHAIN_TRACING_V2: str
    LANGCHAIN_API_KEY: str
    OPENAI_API_KEY: str
    DOC_PATH: str
    RETRIEVER: str
    GOOGLE_API_KEY: str = ''
    GOOGLE_CX_KEY: str = ''
    BING_API_KEY: str = ''
    SEARCHAPI_API_KEY: str = ''
    SERPAPI_API_KEY: str = ''
    SERPER_API_KEY: str = ''
    SEARX_URL: str = ''

#
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Context manager for FastAPI lifespan, to start the background job processor."""
    startup_event()
    scheduled_run_index()
    # await run_index()
    asyncio.create_task(background_job_processor())
    yield

# App initialization
app = FastAPI(lifespan=lifespan)
# app = FastAPI()

# Static files and templates
app.mount("/site", StaticFiles(directory="./frontend"), name="site")
app.mount("/static", StaticFiles(directory="./frontend/static"), name="static")
templates = Jinja2Templates(directory="./frontend")

# WebSocket manager
manager = WebSocketManager()

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#
class ResearchData(BaseModel):
    user_key: str
    data_ref: str


# Constants
DOC_PATH = os.getenv("DOC_PATH", "./my-docs")

#
running_jobs = set()
queue_lock = asyncio.Lock()
job_queue = asyncio.Queue()

async def read_stream(stream, prefix):
    """Read and print lines from an async stream."""
    output = []
    async for line in stream:
        decoded_line = line.decode().strip()
        output.append(decoded_line)
        print(f"{prefix}: {decoded_line}")
    return '\n'.join(output)

async def run_command(root: str):
    """Run the indexing command as an async subprocess."""
    job_id = root
    running_jobs.add(job_id)
    print(f"Running job: {job_id}")

    try:
        process = await asyncio.create_subprocess_exec(
            "graphrag", "index", "--root", root,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout_output, stderr_output = await asyncio.gather(
            read_stream(process.stdout, "stdout"),
            read_stream(process.stderr, "stderr")
        )

        rc = await process.wait()
        print(f"Indexing finished with return code: {rc}")

        return {
            "status": "success" if rc == 0 else "error",
            "message": "Job completed",
            "stdout": stdout_output,
            "stderr": stderr_output
        }
    except Exception as e:
        print(f"Error in run_command: {str(e)}")
        return {"status": "error", "message": str(e)}
    finally:
        running_jobs.remove(job_id)
        await process_next_job()

async def process_next_job():
    """Process the next job in the queue."""
    if not job_queue.empty():
        next_root = await job_queue.get()
        asyncio.create_task(run_command(next_root))

async def background_job_processor():
    """Continuously process jobs from the queue."""
    while True:
        if not job_queue.empty() and len(running_jobs) == 0:
            await process_next_job()
        await asyncio.sleep(1)

# Startup event
@app.on_event("startup")
def startup_event():
    os.makedirs("outputs", exist_ok=True)
    app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")
    os.makedirs(DOC_PATH, exist_ok=True)
    print("startup_event")

@repeat_at(cron="15 */2 * * *")
async def scheduled_run_index():
    print("-----scheduled_run_index-----")
    return await run_index()
# Routes

'''@app.get("/get-items")
async def get_items():
    return items'''

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "report": None})

@app.get("/admin")
async def read_admin_root(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request, "report": None})

@app.post("/research-data")
async def research_data(research_data: ResearchData):
    return await handle_research_data(research_data.user_key, research_data.data_ref)

@app.post("/research-query")
async def research_query(query: str):
    return await handle_research_query(query)

@app.post("/write-final-report")
async def write_final_report(user_key:str):
    return await handle_write_final_report(user_key)

@app.get("/run-index")
async def run_index(root: Optional[str] = "./rag"):
    """Endpoint to start the indexing job."""
    print(f"Received request for /run-index - root: {root}")

    async with queue_lock:
        if root in running_jobs:
            return {"status": "running", "message": "Job is currently running.", "queueSize": job_queue.qsize()}

        await job_queue.put(root)
        if len(running_jobs) == 0:
            asyncio.create_task(process_next_job())
            return {"status": "running", "message": "Job started.", "queueSize": job_queue.qsize()}
        else:
            return {"status": "queued", "message": "Job queued.", "queueSize": job_queue.qsize()}

@app.get("/search-queries")
def fetch_search_queries(user_key:str):
    return handle_fetch_search_queries(user_key)

'''@app.get("/final-report-url")
async def fetch_final_report_url(user_key:str, file_name:str):
    return await handle_fetch_final_report_download_url(user_key, file_name)'''

'''@app.get("/files/")
async def list_files():
    files = os.listdir(DOC_PATH)
    print(f"Files in {DOC_PATH}: {files}")
    return {"files": files}'''


'''@app.post("/api/multi_agents")
async def run_multi_agents():
    return await execute_multi_agents(manager)'''


'''@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    return await handle_file_upload(file, DOC_PATH)'''


'''@app.delete("/files/{filename}")
async def delete_file(filename: str):
    return await handle_file_deletion(filename, DOC_PATH)'''


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        await handle_websocket_communication(websocket, manager)
    except WebSocketDisconnect:
        await manager.disconnect(websocket)

@app.websocket("/adminws")
async def websocket_admin_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        await handle_websocket_communication(websocket, manager)
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
