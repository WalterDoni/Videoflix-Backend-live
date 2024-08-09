from django.contrib import admin
from .models import Video

class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'category')
    search_fields = ('title', 'category')
    list_filter = ('category',)
    ordering = ('-created_at',)

admin.site.register(Video, VideoAdmin)
