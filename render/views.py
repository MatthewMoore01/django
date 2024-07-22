from django.shortcuts import render
from django.http import JsonResponse
import cv2
import numpy as np
import requests
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def capture(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        image = np.asarray(bytearray(file.read()), dtype="uint8")
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)

        filename = 'screenshot.jpg'
        cv2.imwrite(filename, image)
        result = send_screenshot(filename)

        return JsonResponse({'result': result})
    return JsonResponse({'error': 'Invalid request'}, status=400)


def send_screenshot(file_path):
    url = "https://renderapp-h819.onrender.com/identify-lateral-flow-test/"
    with open(file_path, 'rb') as file:
        response = requests.post(url, files={'file': file})
    return response.json().get("result")

# Create your views here.
def index(request):
    return render(request, 'render/index.html', {})