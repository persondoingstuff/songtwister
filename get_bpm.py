#https://github.com/scaperot/the-BPM-detector-python/blob/master/bpm_detection/bpm_detection.py
"""
certifi
contourpy==1.0.7
cycler==0.11.0
fonttools==4.38.0
kiwisolver==1.4.4
matplotlib==3.6.3
numpy==1.24.2
packaging==23.0
Pillow==9.4.0
pyparsing==3.0.9
python-dateutil==2.8.2
PyWavelets==1.4.1
scipy==1.10.0
six==1.16.0

"""


# Copyright 2012 Free Software Foundation, Inc.
#
# This file is part of The BPM Detector Python
#
# The BPM Detector Python is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# The BPM Detector Python is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with The BPM Detector Python; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.


import argparse
import array
import math
import wave
from collections import namedtuple

import numpy
import pywt
from scipy import signal

Audio = namedtuple("Audio", ["samples", "framerate"])

def read_wav(filename: str):
    print("Reading file:", filename)
    # open file, get metadata for audio
    try:
        wavedata = wave.open(filename, "rb")
    except IOError as e:
        print(e)
        return

    # typ = choose_type( wf.getsampwidth() ) # TODO: implement choose_type
    audio_frames = wavedata.getnframes()
    assert audio_frames > 0

    framerate: int = wavedata.getframerate()
    assert framerate > 0

    # Read entire file and make into an array
    samples = list(array.array(
        "i", wavedata.readframes(audio_frames)))

    try:
        assert audio_frames == len(samples)
    except AssertionError:
        print(audio_frames, "not equal to", len(samples))

    print(f"Samples: {len(samples)} - framerate: {framerate}")
    return Audio(samples, framerate)



# simple peak detection
def detect_peak(data: numpy.ndarray) -> numpy.ndarray:
    max_value = numpy.amax(abs(data))
    peak_index = numpy.where(data == max_value)
    # if nothing found then the max must be negative
    if len(peak_index[0]) == 0:
        peak_index = numpy.where(data == -max_value)
    return peak_index


def detect_window_bpm(samples: list, framerate: int) -> numpy.ndarray:
    levels = 4
    wavelet = "db4"
    max_decimation: int = 2 ** (levels - 1)
    min_index = math.floor(60.0 / 220 * (framerate / max_decimation))
    max_index = math.floor(60.0 / 40 * (framerate / max_decimation))
    cA = None

    for level_index in range(levels):
        cA: numpy.ndarray # Approximation coefficient
        cD: numpy.ndarray # Detail coefficient

        # 1) DWT
        if level_index == 0:
            cA, cD = pywt.dwt(data=samples, wavelet=wavelet)
            cD_minlen = len(cD) / max_decimation + 1
            cD_sum = numpy.zeros(math.floor(cD_minlen))
        else:
            cA, cD = pywt.dwt(data=cA, wavelet=wavelet)

        # 2) Filter
        cD = signal.lfilter([0.01], [1 - 0.99], cD)

        # 4) Subtract out the mean.

        # 5) Decimate for reconstruction later.
        cD = abs(cD[:: (2 ** (levels - level_index - 1))])
        cD = cD - numpy.mean(cD)

        # 6) Recombine the signal before ACF
        #    Essentially, each level the detail coefs (i.e. the HPF values)
        #    are concatenated to the beginning of the array
        cD_sum = cD[0 : math.floor(cD_minlen)] + cD_sum

    if not [x for x in cA if x != 0.0]:
        print("No audio data for sample. Skipping...")
        return

    # Adding in the approximate data as well
    cA = abs(signal.lfilter([0.01], [1 - 0.99], cA))
    cA = cA - numpy.mean(cA)
    cD_sum = cA[0 : math.floor(cD_minlen)] + cD_sum

    # ACF
    correlation: numpy.ndarray = numpy.correlate(cD_sum, cD_sum, "full")

    midpoint: int = math.floor(len(correlation) / 2)
    correlation_midpoint_tmp: numpy.ndarray = correlation[midpoint:]
    peak_index = detect_peak(data=correlation_midpoint_tmp[min_index:max_index])
    if len(peak_index) > 1:
        print("No audio data for sample. Skipping...")
        return

    peak_index_adjusted = peak_index[0] + min_index
    window_bpm: numpy.ndarray = 60.0 / peak_index_adjusted * (framerate / max_decimation)
    print(window_bpm)
    return window_bpm


def detect_bpm(samples: list, framerate: int, window: int=3) -> numpy.float64:
    window_sample_count = int(window * framerate)
    max_window_index = math.floor(len(samples) / window_sample_count)
    bpm_items = numpy.zeros(max_window_index)

    # Iterate through all windows
    current_sample_index = 0  # First sample in window_index
    for window_index in range(max_window_index):
        print(window_index, current_sample_index)
        next_sample_index = current_sample_index + window_sample_count

        # Get a new set of samples
        window_samples = samples[current_sample_index:next_sample_index]
        if not ((len(window_samples) % window_sample_count) == 0):
            raise AssertionError(
                f"Number of window samples should be {window_sample_count}, "
                f"but was {len(window_samples)}")

        window_bpm = detect_window_bpm(window_samples, framerate)

        if window_bpm is None:
            continue
        bpm_items[window_index] = window_bpm
        current_sample_index = next_sample_index

    return numpy.median(bpm_items)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process .wav file to determine the Beats Per Minute.")
    parser.add_argument("--filename", required=True, help=".wav file for processing")
    parser.add_argument(
        "--window",
        type=float,
        default=3,
        help="Size of the the window (seconds) that will be scanned to determine the bpm. Typically less than 10 seconds. [3]",
    )

    args = parser.parse_args()
    window = args.window
    audio_data = read_wav(args.filename)

    bpm = detect_bpm(
        samples=audio_data.samples,
        framerate=audio_data.framerate,
        window=window)
    print("Estimated Beats Per Minute:")
    print(bpm)
    print(round(bpm))
