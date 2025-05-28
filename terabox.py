import aiohttp
import logging
from tools import parse_size_to_bytes

# Configure logging
logging.basicConfig(level=logging.ERROR)

async def get_data(url: str):
    """Fetch file data from the Terabox API."""
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"https://wdzone-terabox-api.vercel.app/api?url={url}") as response:
                response.raise_for_status()
                r = await response.json()

                # Log the full response for debugging
                logging.debug(f"API Response: {r}")

                # Check if "📜 Extracted Info" exists and has at least one item
                if r.get("📜 Extracted Info") and len(r["📜 Extracted Info"]) > 0:
                    info = r["📜 Extracted Info"][0]
                    fast_download_link = info.get("🔽 Direct Download Link")
                    video_title = info.get("📂 Title", "Unknown")
                    size = info.get("📏 Size")
                    thumbnail_url = info.get("🖼️ Thumbnails", {}).get("360x270")  # Choose 360x270 thumbnail

                    data = {
                        "file_name": video_title,
                        "link": fast_download_link,
                        "direct_link": fast_download_link,
                        "link": fast_download_link,  # Assuming same link for HD
                        "thumb": thumbnail_url,
                        "size": size,
                        "sizebytes": parse_size_to_bytes(size),
                    }
                    return data
                else:
                    logging.error(f"No '📜 Extracted Info' found in response: {r}")
                    return False

        except aiohttp.ClientResponseError as e:
            logging.error(f"HTTP error fetching data: {e.status} {e.message}")
            return False
        except aiohttp.ClientError as e:
            logging.error(f"Network error fetching data: {e}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error fetching data: {e}")
            return False
