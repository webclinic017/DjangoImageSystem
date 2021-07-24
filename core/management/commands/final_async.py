from django.core.management import BaseCommand
import time
from core.models import ProductPicture, Product, Vendor
import requests
import tempfile
from django.core import files
import concurrent.futures
from django.core.files.base import ContentFile
from PIL import Image
import asyncio
import aiohttp

"""
First Try Finished in 12.52 seconds
Second Try Finished in 12.53 seconds
Third Try Finished in 12.35 seconds
"""
from typing import List, Dict, Any
import async_timeout
import aiofiles
import os
from core.utils import code_gen as generate_hash


class Command(BaseCommand):
    help = "this is a necessary command if its the first time you run project" \
           "this will setup picture and slug and etc"

    @staticmethod
    async def download_file(session: Any, remote_url: str, filename: str) -> None:
        try:
            async with async_timeout.timeout(120):
                async with session.get(remote_url) as response:
                    if response.status == 200:
                        async with aiofiles.open(filename, mode='wb') as f:
                            async for data in response.content.iter_chunked(1024):
                                await f.write(data)
                    else:
                        print(f"Error to get {filename} from Remote Server")
        except asyncio.TimeoutError:
            print(f"Timeout error to download {filename} into Local Server")
            raise


    async def download_files(self, images, path: str) -> None:
        headers = {"user-agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"}
        # connector = aiohttp.TCPConnector(limit=40)
        async with aiohttp.ClientSession(headers=headers) as session:
            tasks = [asyncio.ensure_future(self.download_file(session, image.picture_src, self.get_filename(image, path))) for
                     image
                     in images]
            await asyncio.gather(*tasks)

    def get_filename(self, image, path: str) -> str:
        # image_dir = '{}/{}'.format(path, image.id)
        # image_file = '{}.jpg'.format(generate_hash(image['resource']))
        # image_file = '{}.jpg'.format(generate_hash())
        # image_file = '{}.jpg'.format(image.id)
        file_name = image.picture_src.split('/')[-1]
        # if not os.path.exists(image_dir):
        #     os.makedirs(image_dir)
        return os.path.join(path, file_name)

    def download_images(self, images: List[Dict[str, Any]], path: str) -> None:
        try:
            loop = asyncio.get_event_loop()
            future = asyncio.ensure_future(self.download_files(images, path))
            loop.run_until_complete(future)
            print(f'Images from Remote Server have been downloaded successfully')
        except Exception as error:
            print(f'Error to download images from Remote Server: {error}')
            raise

    # @staticmethod
    # def process_img(obj):
    #
    #     new_image = ContentFile(obj.large.read())
    #     file_name = str(obj.large.name).split('/')[-1]
    #     new_image.name = file_name + '_s'
    #     obj.small = new_image
    #     obj.save()
    #     print('small is saved')
    #     new_image.name = file_name + '_m'
    #     obj.medium = new_image
    #     obj.state = 'published'
    #     obj.save()
    #     print('med is saved')
    #
    # def download(self, obj):
    #     response = requests.get(obj.picture_src, stream=True)
    #
    #     if response.status_code != requests.codes.ok:
    #         pass
    #
    #     file_name = obj.picture_src.split('/')[-1]
    #
    #     lf = tempfile.NamedTemporaryFile()
    #
    #     for block in response.iter_content(1024 * 8):
    #
    #         if not block:
    #             break
    #
    #         lf.write(block)
    #
    #     obj.state = 'downloaded'
    #     obj.large.save(file_name, files.File(lf))
    #
    #     # self.process_img(obj)
    #
    #     print(f' image downloaded url => {obj.picture_src}')
    #
    # def get_tasks(self, session, objs):
    #     tasks = list()
    #     for obj in objs:
    #         tasks.append(session.get(url), ssl=False))
    #
    #
    #
    # async def ays_download(self, obj):
    #     response = requests.get(obj.picture_src, stream=True)
    #
    #     if response.status_code != requests.codes.ok:
    #         pass
    #
    #     file_name = obj.picture_src.split('/')[-1]
    #
    #     lf = tempfile.NamedTemporaryFile()
    #
    #     for block in response.iter_content(1024 * 8):
    #
    #         if not block:
    #             break
    #
    #         lf.write(block)
    #
    #     obj.state = 'downloaded'
    #     obj.large.save(file_name, files.File(lf))
    #
    #     # self.process_img(obj)
    #
    #     print(f' image downloaded url => {obj.picture_src}')

    def initial_setup(self):

        start = time.perf_counter()

        # Product.objects.filter(pictures__state='need_resize')
        pps = list(ProductPicture.objects.filter(state='need_resize')[:50])
        IMAGES_PATH = '/home/amirbahador/Desktop/Pics/'
        self.download_images(pps, IMAGES_PATH)


        # Multi thread

        #
        # print(f'you have {len(pps)} not downloaded image')
        #
        # with concurrent.futures.ThreadPoolExecutor() as executor:
        #     executor.map(self.download, pps)

        # Async Io

        # asyncio.run(self.ays_download(pps))

        finish = time.perf_counter()

        # Time Analyze

        print(f'Finished in {round(finish - start, 2)} seconds')

    def handle(self, *args, **options):
        self.initial_setup()


# multi thereaed  donload and convert Finished in 171.32 seconds
# only download and save large pic Finished in 59.66 seconds