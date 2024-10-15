from django.http import JsonResponse, HttpResponse, Http404
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token
from .models import FileMetadata
import os
import uuid

def csrf(request):
    return JsonResponse({'csrfToken': get_token(request)})

def process_file(file):
    file_id = str(uuid.uuid4())
    file_ext = os.path.splitext(file.name)[1]
    filename = f"{file_id}{file_ext}"
    file_path = os.path.join(settings.MEDIA_ROOT, filename)

    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

    with open(file_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

    FileMetadata.objects.create(
        id=file_id,
        original_name=file.name,  
        file_size=file.size,  
        file_path=file_path
    )

    return file_id

def upload_file(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        if not file:
            return JsonResponse({"error", "No file uploaded"}, status=400)
        
        try: 
            file_id = process_file(file)
            return JsonResponse({"id": file_id}, status=201)
        
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invlaid request"}, status=400)

def upload_multi_files(request):
    if request.method == 'POST':
        files = request.FILES.getlist('files')

        try:
            file_ids = list(map(process_file, files))
            return JsonResponse({"ids": file_ids}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


    return JsonResponse({"error": "Invlaid request"}, status=400)


def get_all(request):
    files = FileMetadata.objects.all().values(
        'id', 'original_name', 'file_size' # , 'upload_date', 'version'
    )
    return JsonResponse(list(files), safe=False)

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

def delete_file(request, file_id):
    try: 
        file_metadata = FileMetadata.objects.get(id=file_id)
        file_path = file_metadata.file_path
        
        if os.path.exists(file_path):
            os.remove(file_path)

        file_metadata.delete()

        return JsonResponse({"message": "File deleted"}, status=200)
    except FileMetadata.DoesNotExist:
        return JsonResponse({"error": "File not found"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
            

