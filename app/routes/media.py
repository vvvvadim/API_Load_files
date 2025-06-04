from fastapi import APIRouter, UploadFile,HTTPException, status,Form,Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from app.func.functions import delete_data,post_data, get_order,post_data_id
from app.config.config import MEDIA_FOLDER, CURRENT_URL
import os
import uuid
import datetime
import aiofiles
from typing import Annotated
from app.database.database import Media

api_router = APIRouter(tags=["Загрузка файлов"])
templates = Jinja2Templates(directory=os.path.abspath(os.path.expanduser('ui')))

@api_router.get("/{tag}", name="main_route")
async def main_func(tag:str,request:Request):
    check = await get_order(tag=tag)
    if check is None:
        return templates.TemplateResponse(name='index1.html', context={'request': request, 'tag': tag })
    else:
        if check.status_order =='NEW':
            return templates.TemplateResponse(name='index3.html', context={'request': request, 'tag': tag, 'media': check.medias })
        else:
            return templates.TemplateResponse(name='status.html', context={'request': request, 'tag': tag})



@api_router.post("/upload")
async def upload_file(tag : Annotated[str, Form()], files: list[UploadFile], request:Request):
    try:
        order = await get_order(tag=tag)
        if len(files) == 1 and files[0].size == 0:
            current_url = CURRENT_URL+tag
            return RedirectResponse(url=current_url, status_code=303)
        else:
            for file in files:
                file_id = (datetime.datetime.now().strftime('%Y-%m-%d-%s')
                           + '-'
                           + str(uuid.uuid4())
                           + '.'
                           + '.'.join(file.filename.split('.')[-1:]))
                file.filename = file_id
                contents = await file.read()
                path = os.path.join(MEDIA_FOLDER, file.filename)
                async with aiofiles.open(path, 'wb') as f:
                    await f.write(contents)
                    await file.close()
            media = [Media(link=i.filename) for i in files]
            if order is None:
                await post_data(tag=tag, files=media)
            else:
                await post_data_id(ord_id=order.id, files=media)

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='There was an error uploading the file',
        )

    return templates.TemplateResponse(name='final.html',context={'request': request, 'tag': tag })


@api_router.get("/api/delete-data",
                     status_code=status.HTTP_200_OK,
                     response_model=None,
                     description="Очистка базы данных",
                     name="Очистка базы данных")
async def delete_alldata():
    res = await delete_data()
    return res
