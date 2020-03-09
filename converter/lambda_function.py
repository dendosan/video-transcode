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


def convert_file(new_height, in_file, out_file):
    # For all files H.264 Video Codec, Video Bitrate Mode "CBR", Scene Detection False,
    # AAC Audio Codec, LC Audio Profile, 2 Audio Channels, Audio Sample Rate 44100, Audio Bitrate Mode "CBR"

    DEFAULT_SETTINGS = ['-i', in_file, '-c:v', 'libx264', '-profile:v', 'main', '-g', '60', '-filter:v', 'fps=29.97', '-c:a', 'aac',
                        '-ac', '2', '-ar', '44100', '-b:a', '128k', '-y']
    CUSTOM_SETTINGS = []
    if new_height == '360':
        CUSTOM_SETTINGS += ['-level:v', '3.0',
                            '-b:v', '1.3M', '-vf', 'scale=640x360']
    if new_height == '480':
        CUSTOM_SETTINGS += ['-level:v', '3.1',
                            '-b:v', '1.8M', '-vf', 'scale=848x480']
    if new_height == '540':
        CUSTOM_SETTINGS += ['-level:v', '3.1',
                            '-b:v', '2.5M', '-vf', 'scale=960x540']
    if new_height == '720':
        CUSTOM_SETTINGS += ['-level:v', '3.1',
                            '-b:v', '3.5M', '-vf', 'scale=1280x720']

    COMMAND = [FFMPEG_STATIC, *DEFAULT_SETTINGS, *CUSTOM_SETTINGS, out_file]

    print(COMMAND)

    p = subprocess.Popen(COMMAND)
    output = p.communicate()
    print(f"Converted {in_file} to new height = {new_height}")
    return output


def clean_tmp_folder():
    print("Cleaning /tmp folder...")
    for root, _, files in os.walk('/tmp'):
        for name in files:
            print(f"Deleting temp file {name}")
            os.remove(os.path.join(root, name))


def lambda_handler(event, context):
    clean_tmp_folder()

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

            new_heights = ['360', '480', '540', '720']

            for new_height in new_heights:

                new_key_path_and_name = f"{orig_key_base}_{new_height}.{extension}"
                new_temp_path_and_name = f"{temp_file_base}_{new_height}.{extension}"

                # [640x360, 848x480, 960x540, 1280x720]
                convert_file(new_height, temp_path_and_name,
                             new_temp_path_and_name)

                print(
                    f"Copying {new_temp_path_and_name} to {target_bucket} bucket")
                with open(new_temp_path_and_name, "rb") as f:
                    s3.upload_fileobj(f, target_bucket, new_key_path_and_name,
                                      ExtraArgs={'ACL': 'public-read'})

            # Clean /tmp folder
            clean_tmp_folder()

        except Exception as e:
            print(e)
            print(f"Error getting object {key} from bucket {source_bucket}")
            raise e
