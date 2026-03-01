from fastapi import APIRouter, UploadFile,HTTPException, status,Form,Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from app.func.functions import post_data, get_order,post_data_id
from app.config.config import MEDIA_FOLDER, CURRENT_URL
import os
import uuid
import datetime
import aiofiles
from PIL import Image
import io
from typing import Annotated, Tuple
from app.database.database import Media
from app.func.functions import check_media
from ttt import photo_lst

api_router = APIRouter(tags=["Загрузка файлов"])
templates = Jinja2Templates(directory=os.path.abspath(os.path.expanduser('ui')))


def compress_image(
        image: Image.Image,
        max_size: Tuple[int, int] = (1920, 1080),
        quality: int = 85,
        format: str = 'JPEG',
        progressive: bool = True
) -> bytes:
    """
    Оптимизирует и сжимает изображение с сохранением пропорций

    Args:
        image: Исходное изображение (PIL Image)
        max_size: Максимальные размеры (ширина, высота) в пикселях
        quality: Качество сжатия (1-100)
        format: Формат выходного файла ('JPEG', 'WEBP' и др.)
        progressive: Использовать прогрессивную загрузку для JPEG

    Returns:
        Байтовое представление сжатого изображения

    Raises:
        ValueError: Если параметры некорректны
    """
    # Проверка параметров
    if not 1 <= quality <= 100:
        raise ValueError("Качество должно быть между 1 и 100")

    # Конвертация для форматов, не поддерживающих прозрачность
    if format in ('JPEG', 'JPG') and image.mode in ('RGBA', 'LA', 'P'):
        image = image.convert('RGB')

    # Изменение размера с сохранением пропорций
    image.thumbnail(max_size, Image.Resampling.LANCZOS)

    # Оптимизированное сохранение в байты
    img_byte_arr = io.BytesIO()
    save_params = {
        'format': format,
        'quality': quality,
        'optimize': True,
        'progressive': progressive
    }

    # Дополнительные параметры для WEBP
    if format == 'WEBP':
        save_params['method'] = 6  # Максимальное сжатие

    image.save(img_byte_arr, **save_params)

    return img_byte_arr.getvalue()

@api_router.get("/{tag}", name="main_route")
async def main_func(tag:str,request:Request):
    check = await get_order(tag=tag)
    if check is None:
        return templates.TemplateResponse(name='index.html', context={'request': request, 'tag': tag })
    else:
        if check.status_order =='NEW':
            photo_lst = [ i.link for i in check.medias if await check_media(i.link) == 'photo']
            video_lst = [i.link for i in check.medias if await check_media(i.link) == 'video']
            return templates.TemplateResponse(name='page_with_pic.html',
                                              context={'request': request, 'tag': tag, 'photo': photo_lst, 'video': video_lst})
        elif check.status_order == 'CLOSED':
            photo_lst = [ i.link for i in check.medias if await check_media(i.link) == 'photo']
            video_lst = [i.link for i in check.medias if await check_media(i.link) == 'video']
            return templates.TemplateResponse(name='page_gallery.html',
                                              context={'request': request, 'tag': tag, 'photo': photo_lst, 'video': video_lst})
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
                if await check_media(file.filename) == 'photo':
                    contents = await file.read()
                    image = Image.open(io.BytesIO(contents))
                    compressed_contents = compress_image(image)
                else:
                      compressed_contents = await file.read()
                # contents = await file.read()
                # image = Image.open(io.BytesIO(contents))
                # compressed_contents = compress_image(image)
                path = os.path.join(MEDIA_FOLDER, file.filename)
                async with aiofiles.open(path, 'wb') as f:
                    await f.write(compressed_contents)
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