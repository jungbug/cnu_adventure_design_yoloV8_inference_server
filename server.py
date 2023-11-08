import os
import json
import tempfile
from PIL import Image
import base64
import requests

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from ultralytics import YOLO

from PIL.Image import Transpose

import matplotlib.pyplot as plt

from flask import Flask, request, jsonify, Response
app = Flask(__name__)  

model = YOLO("./best.pt")



@app.route('/')           
def index():             
    return 'Hello world'  

@app.route('/predict/image', methods=['POST'])
def predict():
    try:
        print(request.files)
        image_file = request.files.get('photo')
        print(image_file)
        if image_file and isinstance(image_file, FileStorage) and image_file.filename.endswith(('.jpg', '.jpeg', '.png')):
            tempDir = tempfile.gettempdir()
            image_path = os.path.join(
                tempDir, secure_filename("temp_image.jpg"))
            print(image_path)
            image_file.save(image_path)

            with open(image_path, 'rb') as f:
                image_data = f.read()
            img = Image.open(image_path)
            im_rotated = img.transpose(Transpose.ROTATE_270)
            im_rotated.save("end.png")
            img = Image.open("end.png")
            print(img)
            img = img.convert('RGB')
            # img.save(image_path, 'JPEG')
            
            results = model(img)

            
            try:
                result_array = []
                    
                for result in results:
                    boxes = result.boxes
                    masks = result.masks
                    probs = result.probs

                box = result[0].boxes

                for r in results:
                    im_array = r.plot()
                    im = Image.fromarray(im_array[..., ::-1])
                    im.save("output_image.png")
                    with open("output_image.png", 'rb') as f:
                        image_data_output = f.read()

                    base64_str = base64.b64encode(image_data_output).decode('utf-8')

                for box in boxes:
                    class_id = result.names[box.cls[0].item()]
                    cords = box.xyxy[0].tolist()
                    cords = [round(x) for x in cords]
                    conf = round(box.conf[0].item(), 2)
                    result_array.append(class_id)
                    print("Object type:", class_id)
                
                print(result_array)
                return jsonify({"result": result_array, "image": base64_str}), 200
            except:
                if(len(result_array) == 0):
                    return jsonify({"error": "No object detected"}), 200
                else:
                    return jsonify({"result": result_array, "image": base64_str}), 200
                
        else:
            return jsonify({"error": "Image file is missing or invalid."}), 400
    except Exception as e:
        print(e)
        return jsonify({"error": "An internal error occurred."}), 500

if __name__ == '__main__':
    app.run('0.0.0.0', port=5050, debug=True)
