from django.shortcuts import render

from django.shortcuts import render
import cv2
import requests
from tkinter import Tk, Label, Button, Frame
from PIL import Image, ImageTk

def capture_and_send(request):
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()
    if ret:
        filename = 'screenshot.jpg'
        cv2.imwrite(filename, frame)
        result = send_screenshot(filename)
        return render(request, 'camera_app/result.html', {'result': result})
    return render(request, 'camera_app/error.html')

def send_screenshot(file_path):
    url = "https://renderapp-h819.onrender.com/identify-lateral-flow-test/"
    with open(file_path, 'rb') as file:
        response = requests.post(url, files={'file': file})
    return response.json().get("result")

def update_gui(result):
    global result_label
    result_label.config(text=f"Result: {result}")

def update_stream():
    global cap, video_label, video_width, video_height

    ret, frame = cap.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (video_width, video_height))
        img = Image.fromarray(frame)
        img = ImageTk.PhotoImage(img)
        video_label.config(image=img)
        video_label.image = img
    root.after(10, update_stream)
