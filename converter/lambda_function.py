import os
import json
import boto3
from urllib.parse import unquote_plus
import uuid
import subprocess

FFMPEG_STATIC = "/opt/ffmpeg-git-20200305-amd64-static/ffmpeg"
FFPROBE_STATIC = "/opt/ffprobe/ffprobe"

s3 = boto3.client('s3')


def get_video_info(fileloc):
    command = [FFPROBE_STATIC,
               '-v', 'fatal',
               '-show_entries', 'stream=width,height,r_frame_rate,duration',
               '-of', 'default=noprint_wrappers=1:nokey=1',
               fileloc, '-sexagesimal']
    ffmpeg = subprocess.Popen(
        command, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    out, err = ffmpeg.communicate()
    # if(err):
    #     print(f"err = {err}")

    return {'file': fileloc,
            'width': int(out[0]),
            'height': int(out[1]),
            'fps': float(out[2]),
            'duration': out[3]}


def convert_file(fileloc):
    # - 640x360 Resolution, Video Bitrate 1300000, Profile "Main", Level 3.0, GOP Size 60, Framerate 29.97, Audio Bitrate 128000
    # - For all files H.264 Video Codec, Video Bitrate Mode "CBR", Scene Detection False,
    #   AAC Audio Codec, LC Audio Profile, 2 Audio Channels, Audio Sample Rate 44100, Audio Bitrate Mode "CBR"
    command = [FFMPEG_STATIC,
               '-i', fileloc,
               '-c:v', 'libx264',
               '-profile:v', 'main',
               '-filter:v', 'fps=29.97',
               '-c:a', 'aac',
               '-ac', '2',
               '-ar', '44100',
               '-b:v', '1.3M',
               '-b:a', '128k',
               '-y',
               '-vf', 'scale=640x360',
               '/tmp/testconverted.mp4'
               ]
    ffmpeg = subprocess.Popen(
        command, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    out, err = ffmpeg.communicate()
    # if(err):
    #     print(f"err = {err}")
    return out


def lambda_handler(event, context):
    for record in event['Records']:
        source_bucket = record['s3']['bucket']['name']
        key = unquote_plus(record['s3']['object']['key'])
        print(f"source_bucket = {source_bucket}")
        print(f"key = {key}")
        target_bucket = 'modifiedvideos'
        copy_source = {'Bucket': source_bucket, 'Key': key}

        try:
            print("Waiting for the file to persist in the source bucket")
            waiter = s3.get_waiter('object_exists')
            waiter.wait(Bucket=source_bucket, Key=key)
            # print("Copying from originalvideos to modifiedvideos")
            # s3.copy_object(Bucket=target_bucket, Key=key, CopySource=copy_source)

            with open('/tmp/test.mp4', 'wb') as f:
                s3.download_fileobj(source_bucket, key, f)
            print(f"/tmp/test.mp4 size = {os.stat('/tmp/test.mp4').st_size}")

            # file_info = get_video_info('/tmp/test.mp4')
            # print(file_info)

            convert_file('/tmp/test.mp4')

            # convert_file_info = get_video_info('/tmp/testconverted.mp4')
            # print(convert_file_info)

            # now copy this to s3 bucket!
            print("Copying from converted file to modifiedvideos bucket")
            with open('/tmp/testconverted.mp4', "rb") as f:
                s3.upload_fileobj(f, target_bucket, key,
                                  ExtraArgs={'ACL': 'public-read'})

        except Exception as e:
            print(e)
            print(f"Error getting object {key} from bucket {source_bucket}")
            raise e
