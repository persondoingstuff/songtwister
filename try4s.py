import logging
from songtwister import SongTwister
from audiosegment_patch import PatchedAudioSegment as AudioSegment
import yaml
import os
from models import *

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
""")


song = SongTwister(**data)
seq = song.make_seq()