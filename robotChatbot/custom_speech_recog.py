#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

import speech_recognition as sr
import math
import collections
import audioop
import wave
import time
import Const
import numpy as np
import sys, os

WAVE_OUTPUT = 'record/record'

energy_threshold = 300
STOP_LISTENING_TIMEOUT = 15
dynamic_energy_adjustment_damping = 0.15
dynamic_energy_ratio = 1.5

# import pyaudio
# p = pyaudio.PyAudio()
# stream = p.open(format =
#     p.get_format_from_width(2),
#     channels = 1,
#     rate = Const.RATE,
#     output = True
# )

class CustomSpeechRecognition(sr.Recognizer):
    def custom_init(self, chunk, sample_rate):
        self.frames = collections.deque()
        self.chunk = chunk
        self.sample_rate = sample_rate
        self.start_speaking = False
        self.stop_speaking = False
        self.elapsed_time = 0

        assert self.pause_threshold >= self.non_speaking_duration >= 0
        self.seconds_per_buffer = float(self.chunk) / self.sample_rate
        self.pause_buffer_count = int(math.ceil(self.pause_threshold / self.seconds_per_buffer)) + 2 # number of buffers of non-speaking audio during a phrase, before the phrase should be considered complete
        self.phrase_buffer_count = int(math.ceil(self.phrase_threshold / self.seconds_per_buffer))  # minimum number of buffers of speaking audio before we consider the speaking audio a phrase
        self.non_speaking_buffer_count = int(math.ceil(self.non_speaking_duration / self.seconds_per_buffer))  # maximum number of buffers of non-speaking audio to retain before and after a phrase
        self.energy_threshold = None

        self.ws_close = False


    def listen_from_bytes(self, buffer, phrase_time_limit):
        try:
            # buffer = b''.join([(chr(0) if x < 250 else x) for x in buffer])
            # stream.write(buffer)
            # read audio input for phrases until there is a phrase that is long enough
            if not self.stop_speaking:
                # store audio input until the phrase starts
                if not self.start_speaking:
                    # handle waiting too long for phrase by raising an exception
                    if len(buffer) != 0:
                        self.elapsed_time += self.seconds_per_buffer
                        self.frames.append(buffer)
                        if len(self.frames) > self.non_speaking_buffer_count:  # ensure we only keep the needed amount of non-speaking buffers
                            self.frames.popleft()
                        # detect whether speaking has started on audio input
                        energy = audioop.rms(buffer, 2)  # energy of the audio signal
                        if energy > self.energy_threshold: 
                            self.pause_count, self.phrase_count = 0, 0
                            self.start_speaking = True
                            self.elapsed_time = 0
                            self.speaking_start_at = time.time()
                            print('Start Speaking - ' + str(self.energy_threshold))
                        elif self.energy_threshold > 300 and 1.75*energy < self.energy_threshold:
                            self.energy_threshold = 0.95 * self.energy_threshold + energy * 0.05

                        # dynamically adjust the energy threshold using asymmetric weighted average
                        if self.dynamic_energy_threshold:
                            damping = self.dynamic_energy_adjustment_damping ** self.seconds_per_buffer  # account for different chunk sizes and rates
                            target_energy = energy * self.dynamic_energy_ratio
                            self.energy_threshold = self.energy_threshold * damping + target_energy * (1 - damping)
                            self.energy_threshold = energy_threshold if self.energy_threshold < energy_threshold else self.energy_threshold
                    else:
                        # print('waiting too long for phrase')
                        pass
                # read audio input until the phrase ends
                else:
                    # handle phrase being too long by cutting off the audio
                    if len(buffer) != 0:
                        self.elapsed_time += self.seconds_per_buffer
                        self.frames.append(buffer)
                        self.phrase_count += 1

                        # check if speaking has stopped for longer than the pause threshold on the audio input
                        energy = audioop.rms(buffer, 2)  # unit energy of the audio signal within the buffer
                        if self.speaking_start_at + STOP_LISTENING_TIMEOUT > time.time():
                            if energy > self.energy_threshold:
                                self.pause_count = 0
                            else:
                                self.pause_count += 1
                            if self.pause_count > self.pause_buffer_count :  # end of the phrase
                                self.phrase_count -= self.pause_count  # exclude the buffers for the pause before the phrase
                                # check how long the detected phrase is, and retry listening if the phrase is too short
                                if self.phrase_count >= self.phrase_buffer_count or len(buffer) == 0 or (phrase_time_limit and self.elapsed_time > phrase_time_limit): 
                                    self.stop_speaking = True # phrase is long enough or we've reached the end of the stream, so stop listening
                                    # obtain frame data
                                    # for i in range(self.pause_count - self.non_speaking_buffer_count): 
                                        # remove extra non-speaking frames at the end
                                        # self.frames.pop()  
                                    frame_data = b"".join(self.frames)
                                    return sr.AudioData(frame_data, self.sample_rate, 2)
                                else:
                                    # print('Phrase is too short ' + str(self.phrase_count) + ":" + str(self.phrase_buffer_count))
                                    pass
                        else:
                            self.stop_speaking = True
                            self.energy_threshold *= 3
                            frame_data = b"".join(self.frames)
                            return sr.AudioData(frame_data, self.sample_rate, 2)
                    else:
                        # print('phrase being too long 2')
                        pass
                    return False
            else:
                self.start_speaking = False
                self.stop_speaking = False
                self.frames = collections.deque()
            return None
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(fname, exc_tb.tb_lineno, e)

    def listen_from_mic(self, source, timeout=None, phrase_time_limit=None):
        try:
            elapsed_time = 0  # number of seconds of audio read
            buffer = b""  # an empty buffer means that the stream has ended and there is no data left to read
            frames = collections.deque()
            while not self.ws_close:
                frames = collections.deque()
                # store audio input until the phrase starts
                while not self.ws_close:
                    # handle waiting too long for phrase by raising an exception
                    elapsed_time += self.seconds_per_buffer

                    buffer = source.stream.read(self.chunk)
                    if len(buffer) == 0: break  # reached end of the stream
                    frames.append(buffer)
                    if len(frames) > self.non_speaking_buffer_count:  # ensure we only keep the needed amount of non-speaking buffers
                        frames.popleft()

                    # detect whether speaking has started on audio input
                    energy = audioop.rms(buffer, source.SAMPLE_WIDTH)  # energy of the audio signal
                    print("Free", energy, self.energy_threshold)
                    if energy > self.energy_threshold: 
                        print('Start speaking')
                        self.start_speaking = True
                        self.stop_speaking = False
                        break
                    elif self.energy_threshold > 300 and 1.75*energy < self.energy_threshold:
                        self.energy_threshold = 0.95 * self.energy_threshold + energy * 0.05
               
                # read audio input until the phrase ends
                pause_count, phrase_count = 0, 0
                phrase_start_time = elapsed_time
                while not self.ws_close:
                    # handle phrase being too long by cutting off the audio
                    elapsed_time += self.seconds_per_buffer

                    buffer = source.stream.read(self.chunk)
                    if len(buffer) == 0: break  # reached end of the stream
                    frames.append(buffer)
                    phrase_count += 1

                    # check if speaking has stopped for longer than the pause threshold on the audio input
                    energy = audioop.rms(buffer, source.SAMPLE_WIDTH)  # unit energy of the audio signal within the buffer

                    # print("Listening", energy, self.energy_threshold)
                    if energy > self.energy_threshold:
                        pause_count = 0
                        # dynamically adjust the energy threshold using asymmetric weighted average
                        if self.dynamic_energy_threshold:
                            damping = self.dynamic_energy_adjustment_damping ** self.seconds_per_buffer  # account for different chunk sizes and rates
                            target_energy = energy * self.dynamic_energy_ratio
                            self.energy_threshold = self.energy_threshold * damping + target_energy * (1 - damping)
                    else:
                        pause_count += 1
                    if pause_count > self.pause_buffer_count:  # end of the phrase
                        print('Stop speaking')
                        self.stop_speaking = True
                        self.energy_threshold *= 3
                        break

                # check how long the detected phrase is, and retry listening if the phrase is too short
                phrase_count -= pause_count  # exclude the buffers for the pause before the phrase
                if phrase_count >= self.phrase_buffer_count or len(buffer) == 0: break  # phrase is long enough or we've reached the end of the stream, so stop listening

            # obtain frame data
            for i in range(pause_count - self.non_speaking_buffer_count): frames.pop()  # remove extra non-speaking frames at the end
            frame_data = b"".join(frames)

            return sr.AudioData(frame_data, self.sample_rate, source.SAMPLE_WIDTH)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(fname, exc_tb.tb_lineno, e)