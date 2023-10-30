import os
import json
import tempfile

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from flask import Flask, request, jsonify, Response
app = Flask(__name__)    

@app.route('/')           
def index():             
    return 'Hello world'  

@app.route('/predict/image', methods=['POST'])
def predict():
    try:
        image_file = request.files.get('photo')
        # processor = ProcessorFood()
        if image_file and isinstance(image_file, FileStorage) and image_file.filename.endswith(('.jpg', '.jpeg', '.png')):
            tempDir = tempfile.gettempdir()
            image_path = os.path.join(
                tempDir, secure_filename("temp_image.jpg"))
            print(image_path)
            image_file.save(image_path)

            with open(image_path, 'rb') as f:
                image_data = f.read()

            return jsonify({"result": "success"}), 200
            # prediction = processor.predictImage(image_data)
            # response = json.dumps({"result": prediction}, ensure_ascii=False)
            # return Response(response, content_type="application/json; charset=utf-8")
        else:
            return jsonify({"error": "Image file is missing or invalid."}), 400
    except Exception as e:
        print(e)
        return jsonify({"error": "An internal error occurred."}), 500

if __name__ == '__main__':# 다른데서 부르면 실행하지 마라는 뜻이다.
    app.run('0.0.0.0', port=5050, debug=True)