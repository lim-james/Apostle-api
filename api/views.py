from django.http import JsonResponse, HttpResponse, Http404
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token
import os
import uuid

def csrf(request):
    return JsonResponse({'csrfToken': get_token(request)})

def upload_file(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        if not file:
            return JsonResponse({"error", "No file uploaded"}, status=400)

        file_id = str(uuid.uuid4())
        file_ext = os.path.splitext(file.name)[1]
        filename = f"{file_id}{file_ext}"

        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

        file_path = os.path.join(settings.MEDIA_ROOT, filename)

        try: 
            with open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            return JsonResponse({"id": file_id}, status=201)
        
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error", "Invlaid request"}, status=400)

def get_file(request, file_id):
    try: 
        files = os.listdir(settings.MEDIA_ROOT)
        matching_files = [f for f in files if f.startswith(file_id)]

        if not matching_files:
            raise FileNotFoundError

        file_path = os.path.join(settings.MEDIA_ROOT, matching_files[0])

        with open(file_path, 'rb') as f:
            return HttpResponse(f.read(), content_type='application/octet-stream')

    except FileNotFoundError:
        raise Http404("File not found")
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
