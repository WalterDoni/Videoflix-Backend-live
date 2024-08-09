from .models import Video
from rest_framework import serializers

class VideoSerializer(serializers.ModelSerializer):
    video_file = serializers.FileField(max_length=None, use_url=True)
    
    class Meta:
        model = Video
        fields = ['title', 'description', 'video_file', 'category']