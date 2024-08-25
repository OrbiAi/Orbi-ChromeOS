import asyncio
import websockets
import aiofiles
import datetime
import os
from PIL import Image
import pytesseract
import time
import re
import aiohttp
import json

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def fixspacedupe(text):
    text = text.replace('\t', ' ').replace('\n', ' ')
    ctext = re.sub(r' +', ' ', text)
    return ctext

async def genai(text):
    aresponse = "not yet"
    try:
        url = 'http://localhost:11434/api/generate'
        data = {
            "system": ("You will be given text, which is seen on someone's computer screen. Your ONLY job is to respond with an assumption of what you think they're doing on their computer.  You shouldn't mention why you think so, you should just say what they're doing, say it clearly, be confident. You should provide it in a documentation-style text, should be 1-6 sentences in a 3rd person view and past simple time, refer to the user as 'user'. You should ONLY say about what the user is currently doing on the MAIN window, unless the other windows are clearly related."),
            "model": "llama3:8b",
            "prompt": text,
            "stream": False
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                try:
                    response.raise_for_status()
                except Exception as e:
                    print(f"Unable to reach Ollama server (is it running?): {e}")
                res = await response.json()
                aresponse = res['response']
    except Exception as e:
        print(e)
    while aresponse == "not yet":
        await asyncio.sleep(1)
    return aresponse

async def gettext(imgpath):
    img = Image.open(imgpath)
    text = pytesseract.image_to_string(img)
    return text

async def save_image(message, path):
        # msg is binary data of jpeg :3
        filename = f'screenie.jpg'
        async with aiofiles.open(os.path.join(path, filename), 'wb') as f:
            await f.write(message)
        return os.path.join(path, filename)
    
async def do_stuff(websocket):
    async for message in websocket:
        print("got image")
        thetime = str(int(time.time()))
        dir2use = os.path.join('data', thetime)
        os.makedirs(dir2use)
        imgdir = await save_image(message, dir2use)
        imgtxt = await gettext(imgdir)
        doing = await genai(imgtxt)
        dt_object = datetime.datetime.fromtimestamp(int(thetime))
        readabletime = dt_object.strftime("%A, %B %d, %Y %I:%M:%S %p")
        activity = {
            'time': int(thetime),
            'activity': doing,
            'took': round(int(time.time()) - int(thetime)),
            'text': str(fixspacedupe('\n'.join(imgtxt.split('\n')[1:]))),
            'focused': f'Capture {readabletime}'
        }
        async with aiofiles.open(os.path.join(dir2use, 'activity.json'), 'w') as f:
            await f.write(json.dumps(activity))
        async with aiofiles.open(os.path.join('templates', 'template.html'), 'r') as file:
            templateh = await file.read()
        templateh = (templateh
            .replace("{{ description }}", str(activity['activity']))
            .replace("{{ date }}", str(readabletime))
            .replace("{{ took }}", str(activity['took']))
            .replace("{{ img }}", str('screenie.jpg'))
        )
        async with aiofiles.open(os.path.join(dir2use, 'activity.html'), 'w', encoding="utf-8") as newfile:
            await newfile.write(templateh)
        print(f"finished in {activity['took']}s")

async def main():
    async with websockets.serve(do_stuff, '0.0.0.0', 8000):
        print('server is running on ws://0.0.0.0:8000')
        await asyncio.Future()

if __name__ == '__main__':
    asyncio.run(main())
