from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import cv2
import numpy as np
import os
import openai
from openai import OpenAI, AssistantEventHandler
from typing_extensions import override

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

@csrf_exempt
def capture(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        image = np.asarray(bytearray(file.read()), dtype="uint8")
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)

        filename = 'screenshot.jpg'
        cv2.imwrite(filename, image)
        result = identify_lateral_flow_test(filename)

        return JsonResponse({'result': result})
    return JsonResponse({'error': 'Invalid request'}, status=400)

def identify_lateral_flow_test(file_path):
    try:
        result = {"result": ""}

        class EventHandler(AssistantEventHandler):
            @override
            def on_text_created(self, text) -> None:
                result["result"] = text

            @override
            def on_text_delta(self, delta, snapshot):
                result["result"] = delta.value

        # Upload the file to OpenAI with the correct purpose
        with open(file_path, "rb") as file:
            uploaded_file = client.files.create(
                file=file,
                purpose='vision'
            )

        # Create a thread
        thread = client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Please identify the result of this lateral flow test."
                        },
                        {
                            "type": "image_file",
                            "image_file": {"file_id": uploaded_file.id}
                        }
                    ]
                }
            ]
        )

        with client.beta.threads.runs.stream(
                thread_id=thread.id,
                assistant_id='asst_zLWEETO02q3El9LXec4PfNJi',
                event_handler=EventHandler(),
        ) as stream:
            stream.until_done()

        # Clean up the saved file
        os.remove(file_path)

        return result["result"]

    except Exception as e:
        return str(e)


def index(request):
    return render(request, 'render/index.html', {})
