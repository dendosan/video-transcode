# Video Transcode

A python excercise in uploading an mp4 file to an s3 bucket and triggering a lambda to convert to various formats

- An MP4 upload UI that uploads a local video file to an AWS S3 bucket.
- An AWS Lambda function that gets triggered by the upload to S3.  This Lambda function should utilize ffmpeg to generate 4 video files with the following characteristics.
  - 1280x720 Resolution, Video Bitrate 3500000, , Profile "Main", Level 3.1, GOP Size 60, Framerate 29.97, Audio Bitrate 128000
  - 960x540 Resolution, Video Bitrate 2500000, , Profile "Main", Level 3.1, GOP Size 60, Framerate 29.97, Audio Bitrate 128000
  - 848x480 Resolution, Video Bitrate 1800000, , Profile "Main", Level 3.1, GOP Size 60, Framerate 29.97, Audio Bitrate 128000
  - 640x360 Resolution, Video Bitrate 1300000, , Profile "Main", Level 3.0, GOP Size 60, Framerate 29.97, Audio Bitrate 128000
- For all files H.264 Video Codec, Video Bitrate Mode "CBR", Scene Detection False, AAC Audio Codec, LC Audio Profile, 2 Audio Channels, Audio Sample Rate 44100, Audio Bitrate Mode "CBR"

## Setup

- Create two s3 buckets names `originalvideos` and `modifiedvideos`
- The `modifiedvideos` bucket must have `Block public access` setting turned **off**

# uploader

Simple python application running flask. A form is rendered allowing the user to input an mp4 file.
Submitting the mp4 causes the file to be uploaded to an s3 bucket called `originalvideos`

## Install and Run

- must have python 3.7 installed.
- pipenv is used to manage python environment

```
$ pipenv --python 3.7
$ pipenv shell
(uploader) bash-3.2$ pipenv install flask
...
(uploader) bash-3.2$ python app.py
 * Serving Flask app "app" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: on
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 159-189-752
```

- The uploader is now running at `http://127.0.0.1:5000`
- Choose a file with extension `.mp4` and click `Upload`
- **Note: Depending on the size of the mp4 (I used short and small ~5MB 30s videos to test) conversion could take 3 minutes or more!**

## Screenshot of running Application

![Screenshot of app 3in width](https://github.com/dendosan/video-transcode/raw/master/docs/images/ApplicationImage1.png)

# converter

An AWS Lambda written in python that is triggered when new files are created in the AWS bucket called `originalvideos`.
Once triggered, ffmpeg is used to generate various formats of the mp4 and places these new videos in AWS bucket called `modifiedvideos`.

## AWS Setup

- Create lambda using Python 3.7 environment. I called mine `VideoConvert`.
- Copy the code in convert/lambda_function.py into the lambda by `Edit code inline`
- For this lambda, there were technical hurdles using ffmpeg. The easiest way I could find around these hurdles was to create two zip files and upload them as two Layers to the lambda. These had to be done in two zip files because of the limitations on size for Layers.

  - **ffmpeg.zip** contains only the **ffmpeg** executable obtained from: `https://johnvansickle.com/ffmpeg/builds/ffmpeg-git-amd64-static.tar.xz`
  - **ffprobe.zip** contains only the **ffprobe** executable from the same tarball.

- Add a Trigger to the lambda that triggers on ObjectCreated events on the `originalvideos` bucket.
- The S3 bucket `modifiedvideos` must have the `Block public access` disabled so the modified videos can be accessible.

# Potential Enhancements

- delete operation from uploader.
- allow the ffmpeg options to be passed in from uploader.
- parallel processing of ffmpeg conversions.
