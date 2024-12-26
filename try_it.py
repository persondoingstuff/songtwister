import logging
from songtwister import SongTwister
import yaml

from get_bpm import *

logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s [%(name)s] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        encoding='utf-8',
        handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# data = {
#     'filename': 'song_data/espresso.mp3',
#     'bpm': 104,
#     'prefix_length_ms': 306,
#     'edit': [
#         {'do': 'trim', 'start': 'prefix', 'end': '0:02', 'fade_in': '0:01', 'fade_out': 2}]}

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
- do: keep
  start: 1
  end: 2
- do: loop
  times: 4
#   duration: "1:01"
  keep_prefix: false
  keep_suffix: false
- do: fade
  fade_in: 1
  fade_out: 0:30
""")

song = SongTwister(**data)

bpm = detect_bpm(song.audio.get_array_of_samples(), song.audio.frame_rate, 3)

bar_s = song.bar_length_ms / 1000

# b = song.edit_trim(start='prefix', end='suffix').save_audio()
# d = song.edit(data.get('edit')).save_audio()
# b = song.edit_trim(start='prefix', end='suffix').edit_trim(start='4', end="16").save_audio()
# b = song.edit_trim(start='prefix')
# c = b.edit_trim(end="1:00")