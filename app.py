from flask import Flask, request, jsonify, render_template, send_file
from pytubefix import YouTube
import os
import threading
from b2_helper import upload_to_b2
from dotenv import load_dotenv

load_dotenv()


app = Flask(__name__)
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Track download status
download_status = {}

DOWNLOAD_BUCKET_NAME = os.getenv("DOWNLOAD_BUCKET_NAME")
def download_and_upload(video_url, filename, filepath, bucket_name):
    try:
        yt = YouTube(video_url,'WEB')
        audio_stream = yt.streams.filter(only_audio=True).first()
        audio_stream.download(output_path=DOWNLOAD_FOLDER, filename=filename)
        upload_to_b2(filepath, filename, bucket_name)
    except Exception as e:
        print(f"Error processing {filename}: {e}")

def download_audio(video_url, vid_id):
    try:
        yt = YouTube(video_url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        filename = f"{vid_id}.mp4"
        filepath = os.path.join(DOWNLOAD_FOLDER, filename)
        audio_stream.download(output_path=DOWNLOAD_FOLDER, filename=filename)
        download_status[vid_id] = "complete"
    except Exception as e:
        download_status[vid_id] = f"error: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    video_url = data.get('videoUrl')
    if not video_url:
        return jsonify({"status": "error", "message": "No video URL provided"}), 400

    try:
        yt = YouTube(video_url)
        vid_id = yt.video_id
        filename = f"{vid_id}.mp4"
        filepath = os.path.join(DOWNLOAD_FOLDER, filename)

        if os.path.exists(filepath):
            return jsonify({"status": "complete", "vidId": vid_id})

        if vid_id not in download_status or "error" in download_status[vid_id]:
            download_status[vid_id] = "downloading"
            thread = threading.Thread(target=download_and_upload, args=(video_url, filename, filepath, os.getenv("DOWNLOAD_BUCKET_NAME")))
            thread.start()

        return jsonify({"status": "downloading", "vidId": vid_id})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/status/<vid_id>', methods=['GET'])
def check_status(vid_id):
    filename = f"{vid_id}.mp4"
    filepath = os.path.join(DOWNLOAD_FOLDER, filename)

    if os.path.exists(filepath):
        return jsonify({"status": "complete", "vidId": vid_id})

    status = download_status.get(vid_id, "not_found")
    return jsonify({"status": status, "vidId": vid_id})


@app.route('/file/<vid_id>', methods=['GET'])
def get_file(vid_id):
    filename = f"{vid_id}.mp4"
    filepath = os.path.join(DOWNLOAD_FOLDER, filename)

    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    else:
        return jsonify({"status": "error", "message": "File not found"}), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
