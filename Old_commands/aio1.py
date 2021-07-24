import os
import asyncio
import aiofiles
import async_timeout

from aiohttp import ClientSession
from generator import generate_hash
from logger import logger
from typing import List, Dict, Any


async def download_file(session: Any, remote_url: str, filename: str) -> None:
    try:
        async with async_timeout.timeout(120):
            async with session.get(remote_url) as response:
                if response.status == 200:
                    async with aiofiles.open(filename, mode='wb') as f:
                        async for data in response.content.iter_chunked(1024):
                            await f.write(data)
                else:
                    logger.error(f"Error to get {filename} from Remote Server")
    except asyncio.TimeoutError:
        logger.error(f"Timeout error to download {filename} into Local Server")
        raise


async def download_files(images: List[Dict[str, Any]], path: str) -> None:
    headers = {"user-agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"}
    async with ClientSession(headers=headers) as session:
        tasks = [asyncio.ensure_future(download_file(session, image['resource'], get_filename(image, path))) for image
                 in images]
        await asyncio.gather(*tasks)


def download_images(images: List[Dict[str, Any]], path: str) -> None:
    try:
        loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(download_files(images, path))
        loop.run_until_complete(future)
        logger.info(f'Images from Remote Server have been downloaded successfully')
    except Exception as error:
        logger.error(f'Error to download images from Remote Server: {error}')
        raise


def get_filename(image: Dict[str, Any], path: str) -> str:
    image_dir = '{}/{}'.format(path, image['id'])
    image_file = '{}.jpg'.format(generate_hash(image['resource']))
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
    return os.path.join(image_dir, image_file)


def main():
    images = [
        {
            'id': '10755431',
            'resource': 'http://image1.jpg'
        },
        {
            'id': '10755432',
            'resource': 'http://image2.jpg'
        },
        {
            'id': '101426201',
            'recurso': 'http://image3.jpg'
        }
    ]
    IMAGES_PATH = '/home/stivenramireza'
    download_images(images, IMAGES_PATH)


if __name__ == "__main__":
    main()