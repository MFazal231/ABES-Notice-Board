import os
import cloudinary
from dotenv import load_dotenv

load_dotenv()

print("ENV CLOUD:", os.getenv("CLOUDINARY_CLOUD_NAME"))
print("ENV KEY:", os.getenv("CLOUDINARY_API_KEY"))
print("ENV SECRET:", os.getenv("CLOUDINARY_API_SECRET"))

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

cfg = cloudinary.config()

print("CFG CLOUD:", cfg.cloud_name)
print("CFG KEY:", cfg.api_key)
print("CFG SECRET:", cfg.api_secret)