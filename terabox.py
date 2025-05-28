import aiohttp
import logging

async def get_data(url: str):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"https://wdzone-terabox-api.vercel.app/api?url={url}") as response:
                response.raise_for_status()
                r = await response.json()

            # Check if "Extracted Info" exists and has at least one item
            if r.get("Extracted Info") and len(r["Extracted Info"]) > 0:
                info = r["Extracted Info"][0]
                fast_download_link = info.get("Direct Download Link")
                video_title = info.get("Title", "Unknown")
                size = info.get("Size")
                thumbnail_url = info.get("Thumbnails", {}).get("360x270")  # Choose a specific thumbnail size

                data = {
                    "file_name": video_title,
                    "link": fast_download_link,
                    "direct_link": fast_download_link,
                    "link": fast_download_link,  # Assuming same link for HD
                    "thumb": thumbnail_url,
                    "size": size,
                    "sizebytes": None,  # API does not provide bytes directly; could parse "Size" if needed
                }
                return data
            else:
                logging.error("No 'Extracted Info' found in response")
                return False

        except Exception as e:
            logging.error(f"Failed to get data: {e}")
            return False
