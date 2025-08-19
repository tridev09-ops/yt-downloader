from yt_dlp import YoutubeDL
from flask import Flask, request, Response, render_template, send_file, jsonify, after_this_request
import subprocess, uuid, os

app = Flask(__name__)

DOWNLOAD_FOLDER='download'
os.makedirs(DOWNLOAD_FOLDER,exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

title=''

# Fetch formats
@app.route("/fetch", methods=["POST"])
def fetch_formats():
    try:
        url=request.json.get("url")
        ext=request.json.get("ext")
        
        if not url:
            return "No URL provided", 400
        if not ext:
            return "No extension provided", 400
        
        global title
        with YoutubeDL() as ydl:
            info= ydl.extract_info(url, download=False)
            
            title=info.get('title')
            thumbnail=info.get('thumbnail')
            
            formats=[]
            if ext=='mp4':
                for f in info['formats']:
                    filesize = f.get('filesize')
                    if filesize:
                        size_mb = round(filesize / 1024**2, 2)
                        size_str = f"{size_mb} MB"
                    else:
                        size_str = "Unknown size"

                    formats.append({"quality":f.get('height'),"size":size_str})
                
                #for f in formats:
                #    print(f["quality"],f["size"])
        
                def parse_size(size_str):
                    try:
                        return float(size_str.split()[0])
                    except (ValueError, AttributeError, IndexError):
                        return -1

                formats = [{
                        "quality": q,
                        "size": max([
                            i["size"] for i in formats
                            if i.get("quality") == q and isinstance(i.get("size"), str) and i["size"] != "unknown size"
                        ],
                        key=parse_size
                    )}
                    for q in sorted({
                        i.get("quality") for i in formats
                        if isinstance(i.get("quality"), int) and i["quality"] >= 240
                    })
                ]   

                return jsonify({"formats": formats,
                    "title": title,
                    "thumbnail": thumbnail})
            
            else:
                return jsonify({"title": title,
                    "thumbnail": thumbnail})
            
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/download")
def download_video():
    try:
        url = request.args.get("url")
        quality = request.args.get("quality")
        ext = request.args.get("ext")
    
        if not url:
            return "No URL provided", 400
        if not quality:
            return "No quality provided", 400
        if not ext:
            return "No extension provided", 400
        
        
        global title
        
        filename = f"{title}.{ext}"
        #filename = f"{uuid.uuid4()}.{ext}"
        
        filepath =os.path.join(DOWNLOAD_FOLDER, filename)
        
        ydl_opts={}
        
        if ext=='mp4':
            ydl_opts = {
                    "format": f"bestvideo[height<={quality}]+bestaudio/best",
                "merge_output_format": "mp4",
                   "outtmpl": filepath
            }
        elif ext=='mp3':
            ydl_opts = {
                    "format": "bestaudio/best",
                    "outtmpl": filepath[:-4],
                    "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",  # kbps
                    }],
            }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        @after_this_request
        def remove_file(response):
            try:
                os.remove(filepath)
                
            except Exception as e:
                app.logger.error("Error removing file: %s", e)
            
            return response

        return send_file(filepath,as_attachment=True)
        
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)