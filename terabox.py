import aiohttp
import logging

async def get_data(url: str):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"https://teraboxvideodownloader.nepcoderdevs.workers.dev/?url={url}") as response:
                response.raise_for_status()
                r = await response.json()

            if r.get("response"):
                file_info = r["response"][0]
                resolutions = file_info["resolutions"]
                fast_download_link = resolutions["Fast Download"]
                HD_link = resolutions["HD Video"]
                thumbnail_url = file_info["thumbnail"]
                video_title = file_info["title"]

                data = {
                    "file_name": video_title,
                    "link": fast_download_link,
                    "direct_link": fast_download_link,
                    "link": HD_link,
                    "thumb": thumbnail_url,
                    "size": None,  # Assuming size is not provided, you can modify this if size is included in the response
                    "sizebytes": None,  # Assuming size in bytes is not provided
                }
                return data 
            else:
                logging.error("No response data found")
                return False

        except Exception as e:
            logging.error(f"Failed to get data: {e}")
            return False

