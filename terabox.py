import aiohttp
import logging

async def get_data(url: str):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"https://alphaapis.org/terabox/v3/dl?url={url}") as response:
                response.raise_for_status()
                r = await response.json()

            if r.get("url"):
                fast_download_link = r["url"]
                HD_link = r["url"]  # Assuming same link, modify if Alpha API provides multiple qualities
                thumbnail_url = r.get("thumbnail")
                video_title = r.get("file_name", "Unknown")

                data = {
                    "file_name": video_title,
                    "link": fast_download_link,
                    "direct_link": fast_download_link,
                    "link": HD_link,
                    "thumb": thumbnail_url,
                    "size": r.get("size"),        # Will be None if not provided
                    "sizebytes": r.get("bytes"),  # Will be None if not provided
                }
                return data
            else:
                logging.error("No response data found")
                return False

        except Exception as e:
            logging.error(f"Failed to get data: {e}")
            return False
