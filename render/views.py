import cv2
import requests
from django.http import JsonResponse
from django.shortcuts import render
from PIL import Image, ImageTk

def capture_and_send(request):
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()
    if ret:
        filename = 'screenshot.jpg'
        cv2.imwrite(filename, frame)
        result = send_screenshot(filename)
        return JsonResponse({'result': result})
    return JsonResponse({'result': 'error'}, status=500)

def send_screenshot(file_path):
    url = "https://renderapp-h819.onrender.com/identify-lateral-flow-test/"
    with open(file_path, 'rb') as file:
        response = requests.post(url, files={'file': file})
    return response.json().get("result")
# Create your views here.
def index(request):
    return render(request, 'render/index.html', {})