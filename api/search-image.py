from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from bs4 import BeautifulSoup
import httpx, json

app = FastAPI()

@app.get("/api/search-image")
async def search_image(q: str = Query(...)):
    query = q.replace(" ", "+")
    url = f"https://www.bing.com/images/search?q={query}&form=HDRSC2"
    headers = {"User-Agent": "Mozilla/5.0"}

    async with httpx.AsyncClient(headers=headers) as client:
        resp = await client.get(url)
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup.find_all("a", class_="iusc"):
            try:
                metadata = json.loads(tag.get("m"))
                image_url = metadata.get("murl")
                if image_url:
                    img_resp = await client.get(image_url, follow_redirects=True)
                    content_type = img_resp.headers.get("content-type", "image/jpeg")
                    return StreamingResponse(img_resp.aiter_bytes(), media_type="image/jpeg")
            except:
                continue
    return {"error": "No image found"}
