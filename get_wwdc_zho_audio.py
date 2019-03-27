from os import mkdir, remove
from os.path import exists, isdir, join
from random import randint
from time import sleep

import m3u8
import requests
from bs4 import BeautifulSoup
from ffmpy import FFmpeg
from moviepy.editor import AudioFileClip, concatenate_audioclips
from videogrep import vtt

# Starting from WWDC 2018, Apple provides Chinese audio for a few videos
baseUrl = 'https://developer.apple.com'

# Get list of videos
r = requests.get(baseUrl + '/videos/wwdc2018/')
soup = BeautifulSoup(r.text, 'lxml')
videoUrls = []
for section in soup.find_all('section', 'row'):
    for video in section.find_all('a', href=True):
        if video['href'] not in videoUrls:
            videoUrls.append(video['href'])

# Deal with eath video if Chinese (zho) audio and subtitles are available
for url in videoUrls:
    sleep(randint(1, 2))
    r = requests.get(baseUrl + url)
    soup = BeautifulSoup(r.text, 'lxml')
    videoUrl = '/'.join(soup.find('video')['src'].split('/')[:-1])

    baseName = videoUrl.split('/')[-1]
    if not isdir(baseName):
        if exists(baseName):
            remove(baseName)
        mkdir(baseName)

    # Get list of audio clips and save them
    if not exists(baseName+'.wav'):
        clips = []
        audioIndex = m3u8.load(videoUrl + '/audio/zho/zho.m3u8')
        if audioIndex.files:
            for fileAudio in audioIndex.files:
                if not exists(join(baseName, fileAudio)):
                    sleep(randint(3, 5))
                    print(videoUrl + '/audio/zho/' + fileAudio)
                    r = requests.get(videoUrl + '/audio/zho/' + fileAudio)
                    with open(join(baseName, fileAudio), 'wb') as f:
                        f.write(r.content)
                FFmpeg(
                    global_options='-y',
                    inputs={join(baseName, fileAudio): None},
                    outputs={join(baseName, fileAudio+'.wav'): None}
                ).run()
                clips.append(AudioFileClip(join(baseName, fileAudio+'.wav'), fps=48000))

            # Concat audio clips and save in one PCM wave format file
            audioClip = concatenate_audioclips(clips)
            audioClip.write_audiofile(baseName+'.wav')
            audioClip.close()

    # Get list of subtitles in VTT format and save them
    if not exists(baseName+'.srt'):
        sentences = []
        subtitleIndex = m3u8.load(videoUrl + '/subtitles/zho/prog_index.m3u8')
        if subtitleIndex.files:
            for fileSeq in subtitleIndex.files:
                sleep(randint(2, 3))
                print(videoUrl + '/subtitles/zho/' + fileSeq)
                r = requests.get(videoUrl + '/subtitles/zho/' + fileSeq)
                sentences = sentences + vtt.parse_auto_sub(r.text)
                with open(join(baseName, fileSeq), 'w') as f:
                    f.write(r.text)

            # Concat subtitles and save in one SRT format file
            subtitle = []
            for sent in sentences:
                sent['words'] = []
                sent['words'].append({'start': sent['start']})
                sent['words'].append({'end': sent['end']})
            for sub in vtt.convert_to_srt(sentences).split('\n'):
                if ' --> ' in sub:
                    subtitle.append(sub.replace('.', ','))
                else:
                    subtitle.append(sub)
            with open(baseName+'.srt', 'w') as f:
                f.write('\n'.join(subtitle))
