import os
from uuid import uuid4
import asyncio

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path

app = FastAPI()

tasks = {}


async def process_file(task_id: str, file_path: str):
    pass


@app.post('/upload')
async def upload(file: UploadFile = File(...)):
    task_id = str(uuid4())
    temp_dir = Path(__file__).parent
    result_path = os.path.join(temp_dir.parent, f'{task_id}.xlsx')
    tasks[task_id] = {
        'status': 'pending',
        'error': None,
        'result_path': result_path
    }
    upload_path = os.path.join(
        temp_dir.parent, 'upload', file.filename)
    with open(upload_path, 'wb') as buffer:
        buffer.write(await file.read())

    asyncio.create_task(process_file(task_id, upload_path))
    return {'task_id': task_id}


@app.get('/status/{task_id}')
async def get_status(task_id: str):
    task = tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail='Задача не найдена')
    response = {
        'task_id': task_id,
        'status': task['status']
    }
    if task['status'] == 'failed':
        response['error'] = task['error']
    return response


@app.get('/result/{task_id}')
async def get_result(task_id: str):
    task = tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail='Задача не найдена')
    if task['status'] != 'success':
        raise HTTPException(status_code=404, detail='Результат не готов')
    return FileResponse(
        path=task['result_path'],
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        filename=f'{task_id}.xlsx'
    )
