from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import cv2
import numpy as np
import os
import tempfile
import openai
from openai import OpenAI, AssistantEventHandler
from typing_extensions import override
from collections import deque, Counter
from datetime import datetime

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Queue to hold the last five results
last_five_results = deque(maxlen=5)
# List to hold all logs
all_logs = []

@csrf_exempt
def capture(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES.get('file')
        image = np.asarray(bytearray(file.read()), dtype="uint8")
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)

        # Use a temporary file to ensure it gets cleaned up properly
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            filename = temp_file.name
            cv2.imwrite(filename, image)

        try:
            result = identify_lateral_flow_test(filename)
            last_five_results.append(result)
            most_common_result = get_most_common_result()

            # Log the result with timestamp
            log_entry = {
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'result': result,
                'most_common_result': most_common_result
            }
            all_logs.append(log_entry)

            return JsonResponse({'result': most_common_result})
        finally:
            if os.path.exists(filename):
                os.remove(filename)

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

        return result["result"]

    except Exception as e:
        return str(e)

def get_most_common_result():
    if not last_five_results:
        return "No results yet"
    counter = Counter(last_five_results)
    most_common_result, _ = counter.most_common(1)[0]
    return most_common_result

def get_logs(request):
    return JsonResponse({'logs': all_logs})

def index(request):
    return render(request, 'render/index.html', {})