from pypdf import PdfReader
import os

path = 'foto/File1.pdf'
password = 'Telegram_Ramen'

reader = PdfReader(path)
reader.decrypt(password)

for i, page in enumerate(reader.pages):
    print(f"Page {i+1}:")
    for j, img in enumerate(page.images):
        print(f"  Image {j+1}: {len(img.data)} bytes, Name: {img.name}")
