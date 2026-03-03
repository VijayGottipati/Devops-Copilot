import os
import time
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from google import genai
from .memory_engine import store_memory

class MeetingAnalysisView(APIView):
    def post(self, request):
        if 'file' not in request.FILES:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)
            
        project_id = request.data.get('project_id', 1)
        video_file = request.FILES['file']
        
        # Save temp file
        temp_path = default_storage.save(f"tmp/{video_file.name}", video_file)
        full_temp_path = default_storage.path(temp_path)
        
        try:
            client = genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))
            
            # Using Google AI File API for massive context
            print(f"Uploading {video_file.name} to Google AI File API...")
            video_upload = client.files.upload(file=full_temp_path)
            
            # Wait for video processing
            while video_upload.state.name == "PROCESSING":
                print('.', end='')
                time.sleep(10)
                video_upload = client.files.get(name=video_upload.name)
            
            if video_upload.state.name == "FAILED":
                raise ValueError("Video processing failed.")

            print("\nAnalyzing meeting...")
            response = client.models.generate_content(
                model='gemini-1.5-flash',
                contents=[
                    video_upload, 
                    "Analyze this meeting recording. Identify what the team is working on, any blockers, and note how the manager speaks/leads."
                ]
            )
            analysis = response.text
            
            # Learn the new persona and state info
            store_memory(project_id, analysis)
            
            return Response({'analysis': analysis}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            if os.path.exists(full_temp_path):
                os.remove(full_temp_path)
