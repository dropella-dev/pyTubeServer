from b2sdk.v2 import *
import os
from dotenv import load_dotenv

load_dotenv()


# Initialize B2 API
def init_b2():
    info = InMemoryAccountInfo()
    b2_api = B2Api(info)

    app_key_id = os.getenv("B2_APP_KEY_ID")
    app_key = os.getenv("B2_APP_KEY")
    b2_api.authorize_account("production", app_key_id, app_key)

    return b2_api

# Upload a file
def upload_to_b2(file_path, file_name, bucket_name):
    print('UPloading to b2')
    b2_api = init_b2()
    bucket = b2_api.get_bucket_by_name(bucket_name)

    with open(file_path, 'rb') as file:
        bucket.upload_bytes(file.read(), file_name)
        print(f"Uploaded {file_name} to B2 bucket: {bucket_name}")
