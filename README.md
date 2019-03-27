# WWDC_zho

Get zho subtitle and audio from WWDC 2018 videos.

## Usage

Depend on ffmpeg installation. Bundled binary in `imageio-ffmpeg` package reports wrong duration on the downloaded AAC files.

```
pip3 install -r requirements.txt
IMAGEIO_FFMPEG_EXE=`which ffmpeg` python3 get_wwdc_zho_audio.py
```
