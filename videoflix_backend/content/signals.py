from content.tasks import convert_480p, convert_720p
from .models import Video
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
import os
import django_rq



@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    if created:
        queue = django_rq.get_queue('default', autocommit=True)
        queue.enqueue(convert_480p,instance.video_file.path)
        queue.enqueue(convert_720p,instance.video_file.path)
      
    
    
@receiver(post_delete, sender=Video)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.video_file:
        if os.path.isfile(instance.video_file.path):
            os.remove(instance.video_file.path)
    delete_generated_videos(instance)


def delete_generated_videos(instance):
    base_name, _ = os.path.splitext(instance.video_file.path)
    resolutions = ['480p', '720p']
    for resolution in resolutions:
        video_path = base_name + f'_{resolution}.mp4'
        if os.path.isfile(video_path):
            os.remove(video_path)
