import os
import subprocess

def convert_480p(source):
    base_name, _ = os.path.splitext(source) 
    new_name = base_name + '_480p.mp4'
    cmd = 'ffmpeg -i "{}" -s hd480 -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"'.format(source, new_name)
    subprocess.run(cmd)
    
def convert_720p(source):
    base_name, _ = os.path.splitext(source)
    new_name = base_name + '_720p.mp4'
    cmd = 'ffmpeg -i "{}" -s hd720 -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"'.format(source, new_name)
    subprocess.run(cmd)
    

