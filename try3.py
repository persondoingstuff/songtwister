import logging
from songtwister import SongTwister
from audiosegment_patch import PatchedAudioSegment as AudioSegment
import yaml
import os


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s [%(name)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8',
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

data = yaml.safe_load("""
filename: song_data/espresso.mp3
bpm: 104
prefix_length_ms: 306
edit:
- do: trim
  start: prefix
  end: suffix
#   - do: trim
#     start: 4
#     end: 32
# - do: keep
#   start: 1
#   end: 2
# - do: loop
#   times: 4
- do: process
  tempo: 130bpm
  pitch: 90%
""")

f1 = [{
    'do': 'test'
}]

f2 = {
    'do': 'mute'
}

f3 = {'group':
        [
            {
            'do': 'pan',
            'pan': 'left',
            'pan_to': 'right'},
            {
            'do': 'reverse',
            'mode': 'bounceback',
            }
        ]
    }

f4 = {
    'do': 'pan',
    'pan': 'left',
    'pan_to': 'right'
}


song = SongTwister(**data)
# logger.info('processing')
# pingo: SongTwister = song.apply_processing(tempo="120bpm")
# pingo = song.edit(data.get('edit'))
# print(pingo.bpm, song.bpm)
# logger.info('processed')
pingo = song.add_processing(f3)
pingo.audio.export("pingo.mp3")
