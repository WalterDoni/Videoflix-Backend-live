from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import Video
import tempfile
from django.core.files.base import ContentFile
import os

class VideoViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        
         # Create a temporary file for the `video_file` field
        self.temp_file = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
        self.temp_file.write(b"test data") # Write some test data to the file
        self.temp_file.seek(0) # Reset file pointer to the beginning
        
         # Create a Video object with the temporary file
        self.video = Video.objects.create(
            title="Test Video",
            description="Test Description",
            video_file=ContentFile(self.temp_file.read(), name="test_video.mp4"),
            category="Test Category"
        )
        self.temp_file.close()
        
        self.url = reverse('video-list')  # The name must match the name in `urls.py`.

    def test_get_videos(self):
        # Test the GET method for the video endpoint
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)   # Use `response.json()` instead of `response.data`.


    def test_post_invalid_video(self):
        # Test posting an invalid video (with an empty title and empty file)
        data = {
            'title': '',  ## Invalid because the title is empty
            'description': 'Invalid Description',
            'video_file': '',  # Empty FileField
            'category': 'Invalid Category'
        }
        response = self.client.post(self.url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.json()) # Check whether the error is present in the response


    def tearDown(self):
        # Delete temporary file
        if hasattr(self, 'temp_file'):
            os.remove(self.temp_file.name)