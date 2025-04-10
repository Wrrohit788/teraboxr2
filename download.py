import aiohttp

async def download_file(url, file_name, progress_callback=None):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            total_size = int(response.headers.get('Content-Length', 0))
            downloaded_size = 0

            with open(file_name, 'wb') as f:
                async for chunk in response.content.iter_chunked(1024):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        if progress_callback:
                            await progress_callback(downloaded_size, total_size)

            return file_name
