import logging
from songtwister import SongTwister
from audiosegment_patch import PatchedAudioSegment as AudioSegment
import yaml
import os

from tempfile import NamedTemporaryFile, TemporaryFile

logging.basicConfig(
        level=logging.DEBUG,
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
# - do: keep
#   start: 1
#   end: 2
# - do: loop
#   times: 4
- do: process
  tempo: 130bpm
  pitch: 90%
""")

song = SongTwister(**data)
logger.info('processing')
# pingo: SongTwister = song.apply_processing(tempo="120bpm")
pingo = song.edit(data.get('edit'))
print(pingo.bpm, song.bpm)
logger.info('processed')
pingo.audio.export("pingo.mp3")

# temp_file_name = None
# # with NamedTemporaryFile(mode="wb", delete=False) as tempo:
# # logger.info(tempo.name)
# # temp_file_name = tempo.name
# logger.info("exporting")
# atempo = '-af "atempo=0.75"'
# rtempo = '-filter:a "rubberband=tempo=0.75"'
# rpitch = '-filter:a "rubberband=pitch=0.75,formant=shifted"'
# bongo = song.audio.process_with_ffmpeg([
#     rpitch
# ])
# # song.audio.export(tempo.name, format='wav', force_full_wav=True, parameters=['-af','\"volume=4\"'])#, parameters=['-filter:a "rubberband=tempo=1.059463094352953"'])
# # print("Rebuilding object")
# # bongo = AudioSegment.from_file(tempo.name)
# logger.info('done')

# # try:
# #     os.unlink(temp_file_name)
# # except FileNotFoundError as e:
# #     print(e)

# print(len(bongo))
# bongo.export("bongo.mp3")

r"""

ffmpeg -y -i C:\Users\admin\Code\public\Songtwister\song_data\cigars_move_it_fade-1-128.mp3 -filter:a "rubberband=tempo=1.059463094352953" -f wav C:\\Users\\admin\\AppData\\Local\\Temp\\tmphv2l5n86

, codec="pcm_s16le"
, parameters=['-filter:a "rubberband=tempo=1.059463094352953"']
"""