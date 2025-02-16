import json
import os
import re
import time
import shutil
from typing import Dict, List, Any
from fastapi.responses import JSONResponse
from gpt_researcher.document.document import DocumentLoader
# Add this import
from backend.utils import write_md_to_pdf, write_md_to_word, write_text_to_md
from gpt_researcher import GPTResearcher
from gpt_writer import GPTTopicWriter
from firebase_admin import credentials, db, initialize_app, storage
import firebase_admin
from .websocket_manager import run_research
import io
from multi_agents.agents import DiagnoseResearchAgent, DietResearchAgent, LifestyleResearchAgent, MedResearchAgent, RelatedDisorderResearchAgent, SportResearchAgent, SymptomResearchAgent, TherapyResearchAgent
def get_firebase_cert():
    return {
      "type": "service_account",
      "project_id": os.getenv('FIREBASE_PROJECT_ID'),
      "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID'),
      "private_key": os.getenv('FIREBASE_PRIVATE_KEY').replace(r'\n', '\n'),
      "client_email": "firebase-adminsdk-1hpoa@chat-psychologist-ai.iam.gserviceaccount.com",
      "client_id": os.getenv('FIREBASE_CLIENT_ID'),
      "auth_uri": "https://accounts.google.com/o/oauth2/auth",
      "token_uri": "https://oauth2.googleapis.com/token",
      "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
      "client_x509_cert_url": os.getenv('FIREBASE_CERT_URL'),
      "universe_domain": "googleapis.com"
    }


def get_user(user_key):
    user_data = db.reference('users').child(user_key).get()
    return user_data

def handle_fetch_search_queries(user_key: str):
    # Initialize Firebase
    cred = credentials.Certificate(get_firebase_cert())
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred, {
            'storageBucket': 'chat-psychologist-ai.appspot.com'
        })

    bucket = storage.bucket()
    blob = bucket.blob(f'research/{user_key}/search_queries')

    try:
        search_queries = blob.download_as_bytes()
        search_queries = search_queries.decode("utf-8")
        print(search_queries)
    except Exception as e:
        print(e)
        search_queries = ''

    search_queries = [f"####{str(list(i.keys())[0])}-{str(list(i.values())[0])}" for i in json.loads(search_queries)]
    return ";".join(search_queries)


async def handle_fetch_final_report_download_url(user_key: str, file_name: str):
    # Initialize Firebase
    cred = credentials.Certificate(get_firebase_cert())
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred, {
            'storageBucket': 'chat-psychologist-ai.appspot.com'
        })

    file_obj = io.BytesIO()

    bucket = storage.bucket()
    blob = bucket.blob(f'research/{user_key}/final_report.md')
    blob.download_to_file(file_obj)

    contents = blob.download_as_bytes()

    print("file_obj", file_obj.seek(0))
    print("file_obj", contents.decode("utf-8"))
    return file_obj


async def handle_write_final_report(user_key: str):
    # Initialize Firebase
    DATABASE_URL = os.getenv('FIREBASE_DATABASE_URL')
    cred = credentials.Certificate(get_firebase_cert())
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred, {
            'databaseURL': DATABASE_URL,
            'storageBucket': 'chat-psychologist-ai.appspot.com'
        })

    try:
        user_data = get_user(user_key)
        search_queries = handle_fetch_search_queries(user_key)
        mental_data = {}
        if user_data.get('personal_info_phase_1_completed', False):
            mental_data.update(user_data.get('personal_info_responses_phase_1', {}))
        if user_data.get('personal_info_phase_2_completed', False):
            mental_data.update(user_data.get('personal_info_responses_phase_2', {}))
        if user_data.get('personal_info_phase_3_completed', False):
            mental_data.update(user_data.get('personal_info_responses_phase_3', {}))
    except Exception as e:
        search_queries = ''
        mental_data = ''
        return e

    researcher = GPTResearcher()
    report = await researcher.write_report(f"What potential mental health issues/disorders stand out from these data together: {search_queries}", mental_data)
    print(researcher.get_data_research_sub_queries())
    report = str(report)
    sanitized_filename = sanitize_filename(f"final_report_{int(time.time())}")
    file_path = await generate_report_files(report, sanitized_filename)

    bucket = storage.bucket()
    blob = bucket.blob(f'research/{user_key}/{sanitized_filename}.md')
    blob.upload_from_filename(file_path)

    blob = bucket.blob(f'research/{user_key}/final_report.md')
    blob.upload_from_filename(file_path)
    return file_path

async def handle_research_questions(user_key:str, data_refs: str):
    # Initialize Firebase
    DATABASE_URL = os.getenv('FIREBASE_DATABASE_URL')
    cred = credentials.Certificate(get_firebase_cert())
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred, {
            'databaseURL': DATABASE_URL,
            'storageBucket': 'chat-psychologist-ai.appspot.com'
        })

    try:
        user_data = get_user(user_key)
        refs = data_refs.split(";")
        q_by_topic = None
        for ref in refs:
            data = user_data.get(ref, {})
            q_by_topic = [{'topic': t, 'content': list(data[t].keys())} for t in data.keys() if data[t]]
            print(q_by_topic)
    except Exception as e:
        print("empty data to research")
        return "error"

    researcher = GPTResearcher()
    await researcher.conduct_question_research(q_by_topic)
    print(researcher.get_data_research_sub_queries())

    return search_queries


async def handle_research_query(query):
    await run_research(json.dumps({'query': query}))

async def handle_research_disorder(query):
    disorders = query.split(";")
    for disorder in disorders:
        await TherapyResearchAgent(disorder=disorder).research()
        #await DiagnoseResearchAgent(disorder=disorder).research()
        #await DietResearchAgent(disorder=disorder).research()
        #await SportResearchAgent(disorder=disorder).research()
        #await RelatedDisorderResearchAgent(disorder=disorder).research()
        #await MedResearchAgent(disorder=disorder).research()
        #await LifestyleResearchAgent(disorder=disorder).research()

async def handle_summarize_data(user_key:str, data_ref: str):
    # Initialize Firebase
    DATABASE_URL = os.getenv('FIREBASE_DATABASE_URL')
    cred = credentials.Certificate(get_firebase_cert())
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred, {
            'databaseURL': DATABASE_URL,
            'storageBucket': 'chat-psychologist-ai.appspot.com'
        })

    try:
        user_data = get_user(user_key)
        data = user_data.get(data_ref, {})
    except Exception as e:
        print("empty data to research")
        return "error"

    print("data", type(data))
    print("data keys", list(data.keys()))
    writer = GPTTopicWriter()

    bucket = storage.bucket()
    blob = bucket.blob(f'research/{user_key}/final_report.md')

    try:
        report = blob.download_as_bytes()
        report = report.decode("utf-8")
        print(report)
    except Exception as e:
        print(e)
        report = ''

    i = 1
    for (topic, topic_data) in data.items():
        print("topic", topic)
        print("topic_data", topic_data)
        data = {}

        for (sub_topic, sub_topic_data) in topic_data.items():
            if isinstance(sub_topic_data, dict) and 'score' in sub_topic_data:
                data[sub_topic] = sub_topic_data['score']
            else:
                data[sub_topic] = sub_topic_data

        print("data", data)
        summaries = await writer.write_report(topic, data)
        #diagnoses = await writer.write_diagnoses(topic, topic_data)
        #report += f"---{summaries}\n\n## Possible disorders\n\n{diagnoses}---\n\n"
        report += f"---{summaries}---\n\n"
        #print('----report----', report)
        if i == 2: break
        i += 1

    report = str(report)
    sanitized_filename = sanitize_filename(f"final_report_{int(time.time())}")
    file_path = await generate_report_files(report, sanitized_filename)

    bucket = storage.bucket()
    blob = bucket.blob(f'research/{user_key}/{sanitized_filename}.md')
    blob.upload_from_filename(file_path)

    blob = bucket.blob(f'research/{user_key}/final_report.md')
    blob.upload_from_filename(file_path)

    return file_path

async def handle_research_data(user_key:str, data_ref: str):
    # Initialize Firebase
    DATABASE_URL = os.getenv('FIREBASE_DATABASE_URL')
    cred = credentials.Certificate(get_firebase_cert())
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred, {
            'databaseURL': DATABASE_URL,
            'storageBucket': 'chat-psychologist-ai.appspot.com'
        })


    bucket = storage.bucket()
    blob = bucket.blob(f'research/{user_key}/search_queries')

    try:
        search_queries = blob.download_as_bytes()
        search_queries = search_queries.decode("utf-8")
        # search_queries = search_queries.split(';')
        search_queries = json.loads(search_queries)
        print(search_queries)
    except Exception as e:
        search_queries = []

    try:
        user_data = get_user(user_key)
        data = user_data.get(data_ref, {})
    except Exception as e:
        print("empty data to research")
        return "error"

    researcher = GPTResearcher()
    await researcher.conduct_data_research(data)
    print(researcher.get_data_research_sub_queries())
    search_queries.extend(researcher.get_data_research_sub_queries())
    # blob.upload_from_string(';'.join(search_queries))
    blob.upload_from_string(json.dumps(search_queries))

    return search_queries

def sanitize_filename(filename: str) -> str:
    return re.sub(r"[^\w\s-]", "", filename).strip()

async def handle_diagnose_command(websocket, data: str, manager):
    json_data = json.loads(data[9:])
    task, report_type, source_urls, tone, headers, report_source = extract_command_data(
        json_data)

    if not task or not report_type:
        print("Error: Missing task or report_type")
        return

    sanitized_filename = sanitize_filename(f"task_{int(time.time())}")

    report = await manager.start_diagnose(
        task, report_type, report_source, source_urls, tone, websocket, headers
    )
    #report = str(report)
    #file_paths = await generate_report_files(report, sanitized_filename)
    #await send_file_paths(websocket, file_paths)

async def handle_research_command(websocket, data: str, manager):
    json_data = json.loads(data[9:])
    task = json_data.get("task")

    if not task:
        print("Error: Missing task or report_type")
        return

    report = await manager.start_research(
        task, websocket
    )
    report = str(report)
    file_paths = await generate_report_files(report, sanitized_filename)
    #await send_file_paths(websocket, file_paths)

async def handle_human_feedback(data: str):
    feedback_data = json.loads(data[14:])  # Remove "human_feedback" prefix
    print(f"Received human feedback: {feedback_data}")
    # TODO: Add logic to forward the feedback to the appropriate agent or update the research state

async def handle_chat(websocket, data: str, manager):
    json_data = json.loads(data[4:])
    print(f"Received chat message: {json_data.get('message')}")
    await manager.chat(json_data.get("message"), websocket)

async def generate_report_files(report: str, filename: str) -> Dict[str, str]:
    #pdf_path = await write_md_to_pdf(report, filename)
    #docx_path = await write_md_to_word(report, filename)
    md_path = await write_text_to_md(report, filename)
    #return {"pdf": pdf_path, "docx": docx_path, "md": md_path}
    return md_path


async def send_file_paths(websocket, file_paths: Dict[str, str]):
    await websocket.send_json({"type": "path", "output": file_paths})


def get_config_dict(
    langchain_api_key: str, openai_api_key: str, tavily_api_key: str,
    google_api_key: str, google_cx_key: str, bing_api_key: str,
    searchapi_api_key: str, serpapi_api_key: str, serper_api_key: str, searx_url: str
) -> Dict[str, str]:
    return {
        "LANGCHAIN_API_KEY": langchain_api_key or os.getenv("LANGCHAIN_API_KEY", ""),
        "OPENAI_API_KEY": openai_api_key or os.getenv("OPENAI_API_KEY", ""),
        "TAVILY_API_KEY": tavily_api_key or os.getenv("TAVILY_API_KEY", ""),
        "GOOGLE_API_KEY": google_api_key or os.getenv("GOOGLE_API_KEY", ""),
        "GOOGLE_CX_KEY": google_cx_key or os.getenv("GOOGLE_CX_KEY", ""),
        "BING_API_KEY": bing_api_key or os.getenv("BING_API_KEY", ""),
        "SEARCHAPI_API_KEY": searchapi_api_key or os.getenv("SEARCHAPI_API_KEY", ""),
        "SERPAPI_API_KEY": serpapi_api_key or os.getenv("SERPAPI_API_KEY", ""),
        "SERPER_API_KEY": serper_api_key or os.getenv("SERPER_API_KEY", ""),
        "SEARX_URL": searx_url or os.getenv("SEARX_URL", ""),
        "LANGCHAIN_TRACING_V2": os.getenv("LANGCHAIN_TRACING_V2", "true"),
        "DOC_PATH": os.getenv("DOC_PATH", "./my-docs"),
        "RETRIEVER": os.getenv("RETRIEVER", ""),
        "EMBEDDING_MODEL": os.getenv("OPENAI_EMBEDDING_MODEL", "")
    }


def update_environment_variables(config: Dict[str, str]):
    for key, value in config.items():
        os.environ[key] = value

async def handle_file_to_index(dest_path: str, DOC_PATH: str):
    from os import walk

    i = 0
    for (dirpath, dirnames, filenames) in walk(DOC_PATH):
        for file in filenames:
            if i < 20:
                file_path = os.path.join(dirpath, file)
                print(f"{file_path} moved to {dest_path}")
                await _move_document(file_path, dest_path)
                i += 1

async def _move_document(file_path: str, dest_path):
    os.rename(file_path, os.path.join(
        dest_path, os.path.basename(file_path)))

async def handle_file_upload(file, DOC_PATH: str) -> Dict[str, str]:
    file_path = os.path.join(DOC_PATH, os.path.basename(file.filename))
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    print(f"File uploaded to {file_path}")

    document_loader = DocumentLoader(DOC_PATH)
    await document_loader.load()

    return {"filename": file.filename, "path": file_path}


async def handle_file_deletion(filename: str, DOC_PATH: str) -> JSONResponse:
    file_path = os.path.join(DOC_PATH, os.path.basename(filename))
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"File deleted: {file_path}")
        return JSONResponse(content={"message": "File deleted successfully"})
    else:
        print(f"File not found: {file_path}")
        return JSONResponse(status_code=404, content={"message": "File not found"})


async def execute_multi_agents(manager) -> Any:
    websocket = manager.active_connections[0] if manager.active_connections else None
    if websocket:
        report = await run_research_task("Is AI in a hype cycle?", websocket, stream_output)
        return {"report": report}
    else:
        return JSONResponse(status_code=400, content={"message": "No active WebSocket connection"})


async def handle_websocket_communication(websocket, manager):
    while True:
        data = await websocket.receive_text()
        if data.startswith("diagnose"):
            await handle_diagnose_command(websocket, data, manager)
        elif data.startswith("research"):
            await handle_research_command(websocket, data, manager)
        elif data.startswith("human_feedback"):
            await handle_human_feedback(data)
        elif data.startswith("chat"):
            await handle_chat(websocket, data, manager)
        else:
            print("Error: Unknown command or not enough parameters provided.")


def extract_command_data(json_data: Dict) -> tuple:
    return (
        json_data.get("task"),
        json_data.get("report_type"),
        json_data.get("source_urls"),
        json_data.get("tone"),
        json_data.get("headers", {}),
        json_data.get("report_source")
    )
