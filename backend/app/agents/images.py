import os
import requests
import tempfile
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)

_USE_CLOUDINARY = bool(os.getenv("CLOUDINARY_CLOUD_NAME"))


def generate_post_image(topic: dict, post_data: dict, ctx: dict, user_id: int, openai) -> list:
    """Generate image via DALL-E 3, upload to Cloudinary (prod) or save locally (dev)."""
    prompt = post_data.get("image_prompt", topic["topic"])
    response = openai.images.generate(
        model="dall-e-3",
        prompt=f"Professional LinkedIn post image. {prompt}. Clean, modern, corporate style. No text.",
        size="1024x1024",
        quality="standard",
        n=1,
    )
    image_url = response.data[0].url
    img_data = requests.get(image_url).content

    if _USE_CLOUDINARY:
        # Upload directly to Cloudinary from bytes
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp.write(img_data)
            tmp_path = tmp.name
        result = cloudinary.uploader.upload(
            tmp_path,
            folder=f"postpilot/user_{user_id}",
            public_id=f"{topic['topic'][:30].replace(' ', '_')}_{os.urandom(4).hex()}",
        )
        os.unlink(tmp_path)
        return [result["secure_url"]]
    else:
        # Local dev fallback
        output_dir = f"output/user_{user_id}/images"
        os.makedirs(output_dir, exist_ok=True)
        filename = f"{topic['topic'][:30].replace(' ', '_')}_{os.urandom(4).hex()}.png"
        path = os.path.join(output_dir, filename)
        with open(path, "wb") as f:
            f.write(img_data)
        return [path]
