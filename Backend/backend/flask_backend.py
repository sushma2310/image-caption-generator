import os
# from PIL import Image

import io
from flask import Flask,Blueprint,request,render_template,jsonify,Response,send_file
import jsonpickle
import numpy as np
import json
import base64

from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer
import torch
from PIL import Image

app = Flask(__name__)



model = VisionEncoderDecoderModel.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
feature_extractor = ViTImageProcessor.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
tokenizer = AutoTokenizer.from_pretrained("nlpconnect/vit-gpt2-image-captioning")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)



max_length = 16
num_beams = 4
gen_kwargs = {"max_length": max_length, "num_beams": num_beams}
def predict_step(image_paths):
  images = []
  for image_path in image_paths:
    i_image = Image.open(image_path)
    if i_image.mode != "RGB":
      i_image = i_image.convert(mode="RGB")

    images.append(i_image)

  pixel_values = feature_extractor(images=images, return_tensors="pt").pixel_values
  pixel_values = pixel_values.to(device)

  output_ids = model.generate(pixel_values, **gen_kwargs)

  preds = tokenizer.batch_decode(output_ids, skip_special_tokens=True)
  preds = [pred.strip() for pred in preds]
  return preds


# predict_step(['doctor.e16ba4e4.jpg']) # ['a woman in a hospital bed with a woman in a hospital bed']


@app.route('/api', methods=['GET','POST'])
def apiHome():
    r = request.method
    if(r=="GET"):
        with open("./text.json") as f:
            data=json.load(f)
        return data
    elif(r=='POST'):
        with open('./sample.jpg',"wb") as fh:
            fh.write(base64.decodebytes(request.data))
        captions=predict_step(["./sample.jpg"])
        cap={"captions":captions[0]}
        with open("./text.json","w") as fjson:
                    json.dump(cap,fjson)
        return cap
    
    else:
        return jsonify({
        "captions":"No response!"
        })  

@app.route('/result')
def sendImage():
    return send_file('./sample.jpg',mimetype='image/jpg')

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5000)