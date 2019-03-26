from os import mkdir
from os.path import isdir, join
from random import random
from time import sleep

import m3u8
import requests
from bs4 import BeautifulSoup
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
    sleep(random(3))
    r = requests.get(baseUrl + url)
    soup = BeautifulSoup(r.text, 'lxml')
    videoUrl = '/'.join(soup.find('video')['src'].split('/')[:-1])

    if not isdir(videoUrl.split('/')[-1]):
        mkdir(videoUrl.split('/')[-1])

    subtitleIndex = m3u8.load(videoUrl + '/subtitles/zho/prog_index.m3u8')
    for fileSeq in subtitleIndex.files:
        sleep(random(2))
        r = requests.get(videoUrl + '/subtitles/zho/' + fileSeq)
        sentences = vtt.parse_auto_sub(r.text)
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
        with open(join(videoUrl.split('/')[-1], fileSeq), 'w') as f:
            f.write(r.text)
        with open(join(videoUrl.split('/')[-1], fileSeq+'.srt'), 'w') as f:
            f.write('\n'.join(subtitle))

    audioIndex = m3u8.load(videoUrl + '/audio/zho/zho.m3u8')
    for fileAudio in audioIndex.files:
        sleep(random(2))
        r = requests.get(videoUrl + '/audio/zho/' + fileAudio)
        with open(join(videoUrl.split('/')[-1], fileAudio), 'wb') as f:
            f.write(r.content)
