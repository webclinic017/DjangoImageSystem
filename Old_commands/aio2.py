import aiohttp
import aiofiles

async with aiohttp.ClientSession() as session:
    url = "http://host/file.img"
    async with session.get(url) as resp:
        if resp.status == 200:
            f = await aiofiles.open('/some/file.img', mode='wb')
            await f.write(await resp.read())
            await f.close()