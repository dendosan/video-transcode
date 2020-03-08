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
    out, _ = ffmpeg.communicate()

    return {'file': fileloc,
            'width': int(out[0]),
            'height': int(out[1]),
            'fps': float(out[2]),
            'duration': out[3]}


# For all files H.264 Video Codec, Video Bitrate Mode "CBR", Scene Detection False,
# AAC Audio Codec, LC Audio Profile, 2 Audio Channels, Audio Sample Rate 44100, Audio Bitrate Mode "CBR"
def convert_file_360(file_name, file_loc):
    # 640x360 Resolution, Video Bitrate 1300000, Profile "Main", Level 3.0, GOP Size 60, Framerate 29.97, Audio Bitrate 128000
    command = [FFMPEG_STATIC, '-i', file_loc, '-c:v', 'libx264', '-profile:v', 'main', '-level:v', '3.0', '-g', '60', '-filter:v', 'fps=29.97', '-c:a', 'aac',
               '-ac', '2', '-ar', '44100', '-b:v', '1.3M', '-b:a', '128k', '-y', '-vf', 'scale=640x360', file_name]
    p = subprocess.Popen(command)
    output = p.communicate()
    return output


def convert_file_720(file_name, file_loc):
    # 1280x720 Resolution, Video Bitrate 3500000, , Profile "Main", Level 3.1, GOP Size 60, Framerate 29.97, Audio Bitrate 128000
    command = [FFMPEG_STATIC, '-i', file_loc, '-c:v', 'libx264', '-profile:v', 'main', '-level:v', '3.1', '-g', '60', '-filter:v', 'fps=29.97', '-c:a', 'aac',
               '-ac', '2', '-ar', '44100', '-b:v', '3.5M', '-b:a', '128k', '-y', '-vf', 'scale=1280x720', file_name]
    p = subprocess.Popen(command)
    output = p.communicate()
    return output


def convert_file_540(file_name, file_loc):
    # 960x540 Resolution, Video Bitrate 2500000, , Profile "Main", Level 3.1, GOP Size 60, Framerate 29.97, Audio Bitrate 128000
    command = [FFMPEG_STATIC, '-i', file_loc, '-c:v', 'libx264', '-profile:v', 'main', '-level:v', '3.1', '-g', '60', '-filter:v', 'fps=29.97', '-c:a', 'aac',
               '-ac', '2', '-ar', '44100', '-b:v', '2.5M', '-b:a', '128k', '-y', '-vf', 'scale=960x540', file_name]
    p = subprocess.Popen(command)
    output = p.communicate()
    return output


def convert_file_480(file_name, file_loc):
    # 848x480 Resolution, Video Bitrate 1800000, , Profile "Main", Level 3.1, GOP Size 60, Framerate 29.97, Audio Bitrate 128000
    command = [FFMPEG_STATIC, '-i', file_loc, '-c:v', 'libx264', '-profile:v', 'main', '-level:v', '3.1', '-g', '60', '-filter:v', 'fps=29.97', '-c:a', 'aac',
               '-ac', '2', '-ar', '44100', '-b:v', '1.8M', '-b:a', '128k', '-y', '-vf', 'scale=848x480', file_name]
    p = subprocess.Popen(command)
    output = p.communicate()
    return output


def lambda_handler(event, context):
    print("Clearing /tmp folder...")
    for root, dirs, files in os.walk('/tmp'):
        for name in files:
            print(f"Deleting temp file {name}")
            os.remove(os.path.join(root, name))

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
            orig_key_base, extension = key.rsplit('.', 1)

            temp_path_and_name = '/tmp/temp.mp4'
            temp_file_base, extension = temp_path_and_name.rsplit('.', 1)
            with open(temp_path_and_name, 'wb') as f:
                s3.download_fileobj(source_bucket, key, f)
            print(
                f"{temp_path_and_name} size = {os.stat(temp_path_and_name).st_size}")

            # file_info = get_video_info('/tmp/test.mp4')
            # print(file_info)

            # temp_path_and_name = /tmp/temp.mp4
            # temp_file_base = /tmp/temp
            # new_temp_path_and_name = /tmp/temp_<NewFormat>.mp4

            # key = /uploads/<VideoName>.mp4
            # orig_key_base = /uploads/<VideoName>
            # extension = mp4
            # new_key_path_and_name should be /uploads/<VideoName>_<NewFormat>.mp4

            # 640x360
            new_key_path_and_name = f"{orig_key_base}_360.{extension}"
            new_temp_path_and_name = f"{temp_file_base}_360.{extension}"
            convert_file_360(new_temp_path_and_name, temp_path_and_name)
            print(f"Converted {temp_path_and_name} to scale=640x360")
            print(
                f"Copying {new_temp_path_and_name} to {target_bucket} bucket")
            with open(new_temp_path_and_name, "rb") as f:
                s3.upload_fileobj(f, target_bucket, new_key_path_and_name,
                                  ExtraArgs={'ACL': 'public-read'})

            # 848x480
            new_key_path_and_name = f"{orig_key_base}_480.{extension}"
            new_temp_path_and_name = f"{temp_file_base}_480.{extension}"
            convert_file_480(new_temp_path_and_name, temp_path_and_name)
            print(f"Converted {temp_path_and_name} to scale=848x480")
            print(
                f"Copying {new_temp_path_and_name} to {target_bucket} bucket")
            with open(new_temp_path_and_name, "rb") as f:
                s3.upload_fileobj(f, target_bucket, new_key_path_and_name,
                                  ExtraArgs={'ACL': 'public-read'})

            # 960x540
            new_key_path_and_name = f"{orig_key_base}_540.{extension}"
            new_temp_path_and_name = f"{temp_file_base}_540.{extension}"
            convert_file_540(new_temp_path_and_name, temp_path_and_name)
            print(f"Converted {temp_path_and_name} to scale=960x540")
            print(
                f"Copying {new_temp_path_and_name} to {target_bucket} bucket")
            with open(new_temp_path_and_name, "rb") as f:
                s3.upload_fileobj(f, target_bucket, new_key_path_and_name,
                                  ExtraArgs={'ACL': 'public-read'})

            # 1280x720
            new_key_path_and_name = f"{orig_key_base}_720.{extension}"
            new_temp_path_and_name = f"{temp_file_base}_720.{extension}"
            convert_file_720(new_temp_path_and_name, temp_path_and_name)
            print(f"Converted {temp_path_and_name} to scale=1280x720")
            print(
                f"Copying {new_temp_path_and_name} to {target_bucket} bucket")
            with open(new_temp_path_and_name, "rb") as f:
                s3.upload_fileobj(f, target_bucket, new_key_path_and_name,
                                  ExtraArgs={'ACL': 'public-read'})

            # Clear /tmp folder
            print("Clearing /tmp folder...")
            for root, dirs, files in os.walk('/tmp'):
                for name in files:
                    print(f"Deleting temp file {name}")
                    os.remove(os.path.join(root, name))
        except Exception as e:
            print(e)
            print(f"Error getting object {key} from bucket {source_bucket}")
            raise e
