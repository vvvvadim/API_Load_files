from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload
from app.database.database import engine, Base, connection, Order, Media
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.shemas import OrderSCH
from typing import List
from app.config.config import MEDIA_FOLDER
import os


@connection
async def get_order(session:AsyncSession,tag:str) -> OrderSCH | None:
    res = await session.execute(select(Order)
                                .where(Order.order_name == tag)
                                .options(joinedload(Order.medias)
                                         ))
    res = res.unique().scalar_one_or_none()
    return res


@connection
async def post_data(session:AsyncSession, tag:str, files:list):
    try:
        order = Order(order_name=tag, medias=files)
        session.add(order)
        await session.commit()
    except Exception as e:
        print(e)

@connection
async def post_data_id(session:AsyncSession, ord_id:int, files:list) -> None:
    try:
        order = await session.execute(select(Order)
                                      .filter(Order.id == ord_id)
                                      .options(joinedload(Order.medias))
                                      )
        order = order.unique().scalars().one_or_none()
        order.medias = order.medias + files
        await session.commit()
    except Exception as e:
        print(e)


@connection
async def get_orders(session:AsyncSession) -> List[OrderSCH] | None:
    try:
        res = await session.execute(select(Order)
                                    .filter(Order.status_order == 'NEW' )
                                    .join(Media)
                                    .where(Media.status == 'NEW')
                                    .options(selectinload(Order.medias))
                                    )
        res = res.unique().scalars().all()

        for i in res:
            media_list = list()
            for r in i.medias:
                if r.status == 'NEW':
                    media_list.append(r)
            i.medias = media_list
        return res
    except Exception as e:
        print(e)


@connection
async def change_order_status(session:AsyncSession,
                              tag : str,
                              status_media:str = None,
                              status_order: str = None) -> OrderSCH :
    order = await session.execute(select(Order)
                                  .filter(Order.order_name == tag)
                                  .options(joinedload(Order.medias))
                                  )
    order = order.unique().scalars().one_or_none()
    if order is not None:
        if status_order and status_media is not None:
            order = await set_status_order(order=order, status_ord=status_order)
            order = await set_status_media(order=order, status_m=status_media)
        elif status_order is not None:
            order = await set_status_order(order=order, status_ord=status_order)
        elif status_media is not None:
            order = await set_status_media(order=order, status_m=status_media)
    await session.commit()
    return order


async def set_status_order(order:OrderSCH, status_ord:str) -> OrderSCH :
    order.status_order = status_ord
    if order.status_order == 'CLOSED':
        order = await set_status_media(order=order, status_m='ACCEPTED')
    elif order.status_order == 'DELETED':
        order = await set_status_media(order=order, status_m='DELETED')
    return order

async def set_status_media(order:OrderSCH, status_m:str) -> OrderSCH :
    if status_m == 'ACCEPTED':
        media_list = list()
        for r in order.medias:
            if r.status == 'NEW':
                media_list.append(r.link)
                r.status = status_m
    elif status_m == 'DELETED':
        media_list = list()
        for r in order.medias:
            media_list.append(r.link)
            r.status = status_m
        await delete_media(files=media_list)
    order.status_media = status_m
    return order


async def delete_media(files : list):
    try:
        for file in files:
            file_path = os.path.join(MEDIA_FOLDER, file)
            os.remove(file_path)

    except Exception as e:
            print(e)


async def check_media(filename):
    image_extensions = (
        '.jpg', '.jpeg', '.jpe', '.jfif',  # JPEG
        '.png',  # PNG
        '.gif',  # GIF
        '.bmp', '.dib',  # BMP
        '.tif', '.tiff',  # TIFF
        '.webp',  # WebP
        '.ico',  # ICO
        '.svg',  # SVG (векторный)
        '.heic', '.heif',  # HEIF/HEIC (современные форматы)
        '.avif',  # AVIF
        '.jp2', '.j2k', '.jpf', '.jpx', '.jpm',  # JPEG 2000
        '.pcx',  # PCX
        '.ppm', '.pgm', '.pbm', '.pnm',  # Netpbm форматы
        '.blp',  # BLP (Blizzard)
        '.cur',  # Cursor
        '.dds',  # DirectDraw Surface
        '.fli', '.flc',  # FLI/FLC анимация
        '.fpx',  # FlashPix
        '.fits',  # FITS
        '.gd', '.gd2',  # GD
        '.im',  # IM
        '.mpeg', '.mpg',  # MPEG
        '.msp',  # MSP
        '.palm', '.pdb', '.prc',  # Palm pixmap
        '.pdf',  # PDF (чтение)
        '.psd',  # Photoshop
        '.qoi',  # Quite OK Image
        '.sgi',  # SGI
        '.tga',  # TGA
        '.xbm',  # X BitMap
        '.xpm'  # X PixMap
    )

    video_extensions = (
        # MP4 и производные
        '.mp4', '.m4v', '.m4p', '.m4b',  # MPEG-4 Part 14
        '.mpg', '.mpeg', '.mpe', '.mpv', '.m1v', '.m2v', '.mp2', '.m2p',  # MPEG-1/2
        '.mts', '.m2ts', '.mt2s', '.ts',  # MPEG Transport Stream
        '.tp', '.trp',  # MPEG Transport Stream (другие)
        '.vob',  # DVD Video Object

        # AVI и производные
        '.avi',  # Audio Video Interleave

        # MOV и QuickTime
        '.mov', '.qt',  # QuickTime Movie
        '.hdmov',  # HD QuickTime Movie

        # MKV и Matroska
        '.mkv', '.mk3d', '.mka', '.mks',  # Matroska

        # WebM
        '.webm',  # WebM

        # Windows Media
        '.wmv', '.asf',  # Windows Media Video

        # Flash Video
        '.flv', '.f4v', '.f4p', '.f4a', '.f4b',  # Flash Video

        # 3GP (мобильные)
        '.3gp', '.3g2', '.3gpp', '.3gpp2',  # 3GPP

        # Ogg
        '.ogv', '.ogg', '.ogm',  # Ogg Video

        # RealMedia
        '.rm', '.rmvb', '.ra', '.ram',  # RealMedia

        # Bink Video
        '.bik', '.bik2', '.bk2',  # Bink Video

        # DivX
        '.divx',  # DivX

        # MPEG-4 (другие)
        '.mp4v', '.mpv4', '.m4v',  # MPEG-4 Video

        # MXF (профессиональный)
        '.mxf',  # Material Exchange Format

        # DVR-MS (Windows Media Center)
        '.dvr-ms', '.wtv',  # DVR-MS

        # AVCHD
        '.m2ts', '.mts',  # AVCHD

        # QuickTime (другие)
        '.qtch', '.qtz',  # QuickTime Components

        # DVD
        '.ifo', '.vob',  # DVD files

        # XviD
        '.xvid',  # XviD

        # H.264 / H.265
        '.h264', '.h265', '.264', '.265',  # Raw H.264/H.265
        '.hevc',  # HEVC

        # Matroska 3D
        '.mk3d',  # Matroska 3D
    )
    if filename.lower().endswith(image_extensions):
        return 'photo'
    elif filename.lower().endswith(video_extensions):
        return 'video'
    else:
        return False