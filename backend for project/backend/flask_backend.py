import os
import cv2
import io
import json
import base64
import numpy as np
from flask import Flask,Blueprint,request,render_template,jsonify,Response,send_file
import jsonpickle

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

def predict_step(images):
    pixel_values = feature_extractor(images=images, return_tensors="pt").pixel_values
    pixel_values = pixel_values.to(device)
    output_ids = model.generate(pixel_values, **gen_kwargs)
    preds = tokenizer.batch_decode(output_ids, skip_special_tokens=True)
    preds = [pred.strip() for pred in preds]
    return preds

def video_to_frames(video_path):
    vidcap = cv2.VideoCapture(video_path)
    success,image = vidcap.read()
    frames = []
    while success:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        frames.append(image)
        success, image = vidcap.read()
    return frames

def predict_video_step(video_path):
    frames = video_to_frames(video_path)
    captions = predict_step(frames)
    return captions

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
        captions=predict_step([Image.open("./sample.jpg")])
        cap={"captions":captions[0]}
        with open("./text.json","w") as fjson:
            json.dump(cap,fjson)
        return cap
    else:
        return jsonify({
            "captions":"No response!"
        })

@app.route('/api_video', methods=['POST'])
def apiVideoHome():
    if request.method=='POST':
        with open('./sample.mp4', "wb") as fh:
            fh.write(base64.decodebytes(request.data))
        captions = predict_video_step("./sample.mp4")
        cap = {"captions": captions}
        with open("./text_video.json", "w") as fjson:
            json.dump(cap, fjson)
        return cap
    else:
        return jsonify({
            "captions":"No response!"
        })

@app.route('/result')
def sendImage():
    return send_file('./sample.jpg',mimetype='image/jpg')

@app.route('/result_video')
def sendVideo():
    return send_file('./sample.mp4', mimetype='video/mp4')

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5000)
