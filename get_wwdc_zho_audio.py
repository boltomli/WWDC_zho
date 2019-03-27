from os import mkdir
from os.path import isdir, join
from random import randint
from time import sleep

import m3u8
import requests
from bs4 import BeautifulSoup
from moviepy.editor import AudioFileClip, concatenate_audioclips
from videogrep import vtt

baseUrl = 'https://developer.apple.com'

# Get list of videos
r = requests.get(baseUrl + '/videos/wwdc2018/')
soup = BeautifulSoup(r.text, 'lxml')
videoUrls = []
for section in soup.find_all('section', 'row'):
    for video in section.find_all('a', href=True):
        if video['href'] not in videoUrls:
            videoUrls.append(video['href'])

for url in videoUrls:
    sleep(randint(1, 3))
    r = requests.get(baseUrl + url)
    soup = BeautifulSoup(r.text, 'lxml')
    videoUrl = '/'.join(soup.find('video')['src'].split('/')[:-1])

    baseName = videoUrl.split('/')[-1]
    if not isdir(baseName):
        mkdir(baseName)

    sentences = []

    subtitleIndex = m3u8.load(videoUrl + '/subtitles/zho/prog_index.m3u8')
    for fileSeq in subtitleIndex.files:
        sleep(randint(1, 2))
        r = requests.get(videoUrl + '/subtitles/zho/' + fileSeq)
        sentences = sentences + vtt.parse_auto_sub(r.text)
        with open(join(baseName, fileSeq), 'w') as f:
            f.write(r.text)

    for sent in sentences:
        sent['words'] = []
        sent['words'].append({'start': sent['start']})
        sent['words'].append({'end': sent['end']})
    subs = vtt.convert_to_srt(sentences)

    subtitle = []
    for sub in subs.split('\n'):
        if ' --> ' in sub:
            subtitle.append(sub.replace('.', ','))
        else:
            subtitle.append(sub)
    with open(baseName+'.srt', 'w') as f:
        f.write('\n'.join(subtitle))

    clips = []
    audioIndex = m3u8.load(videoUrl + '/audio/zho/zho.m3u8')
    for fileAudio in audioIndex.files:
        sleep(randint(1, 2))
        r = requests.get(videoUrl + '/audio/zho/' + fileAudio)
        with open(join(baseName, fileAudio), 'wb') as f:
            f.write(r.content)
        clips.append(AudioFileClip(join(baseName, fileAudio)))
    audioClip = concatenate_audioclips(clips)
    audioClip.write_audiofile(baseName+'.wav')
