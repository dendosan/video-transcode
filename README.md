# Video Transcode

A python excercise in uploading an mp4 file to an s3 bucket and triggering a lambda to convert to various formats

- An MP4 upload UI that uploads a local video file to an AWS S3 bucket.
- An AWS Lambda function that gets triggered by the upload to S3.  This Lambda function should utilize ffmpeg to generate 4 video files with the following characteristics.
      - 1280x720 Resolution, Video Bitrate 3500000, , Profile "Main", Level 3.1, GOP Size 60, Framerate 29.97, Audio Bitrate 128000
      - 960x540 Resolution, Video Bitrate 2500000, , Profile "Main", Level 3.1, GOP Size 60, Framerate 29.97, Audio Bitrate 128000
      - 848x480 Resolution, Video Bitrate 1800000, , Profile "Main", Level 3.1, GOP Size 60, Framerate 29.97, Audio Bitrate 128000
      - 640x360 Resolution, Video Bitrate 1300000, , Profile "Main", Level 3.0, GOP Size 60, Framerate 29.97, Audio Bitrate 128000
      - For all files H.264 Video Codec, Video Bitrate Mode "CBR", Scene Detection False, AAC Audio Codec, LC Audio Profile, 2 Audio Channels, Audio Sample Rate 44100, Audio Bitrate Mode "CBR"

## uploader

Simple python application running flask. A form is rendered allowing the user to input an mp4 file.
Submitting the mp4 causes the file to be uploaded to an s3 bucket called "originalvideos"

## converter

An AWS Lambda written in python that is triggered when new files are created in the AWS bucket called "originalvideos".
Once triggered, ffmpeg is used to generate various formats of the mp4 and places these new videos in AWS bucket called "modifiedvideos".
