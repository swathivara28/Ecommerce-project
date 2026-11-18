
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET")

if not SUPABASE_URL or not SUPABASE_KEY or not SUPABASE_BUCKET:
    raise ValueError("Supabase Storage configuration missing in .env")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def upload_product_image(file, filename):

    try:
        file_data = file.read()

        response = supabase.storage.from_(SUPABASE_BUCKET).upload(
            path=filename,
            file=file_data,
            file_options={
                "content-type": file.content_type,
                "upsert": "true"
            }
        )

        image_url = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(filename)

        return True, image_url

    except Exception as e:
        return False, str(e)

if __name__ == "__main__":
    print("Supabase Storage Connected Successfully!")