import numpy as np
import pyaudio
import os
import wave
import audioop
from collections import deque
import time
import math

class SpeechDetector:
    def __init__(self):
        #rospy.init_node('speech_to_text', anonymous=True)

        #rospy.Subscriber("all_control", String, self.cmd_callback)
        #self.speech_pub = rospy.Publisher("edwin_decoded_speech", String)
        #self.speech_status_pub = rospy.Publisher("edwin_stt_status", String)

        self.keyword_detect = True
        self.detect = True

        # Microphone stream config.
        self.CHUNK = 1024  # CHUNKS of bytes to read each time from mic
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000

        self.SILENCE_LIMIT = 1.5  # Silence limit in seconds. The max ammount of seconds where
                           # only silence is recorded. When this time passes the
                           # recording finishes and the file is decoded

        self.PREV_AUDIO = 0.5  # Previous audio (in seconds) to prepend. When noise
                          # is detected, how much of previously recorded audio is
                          # prepended. This helps to prevent chopping the beginning
                          # of the phrase.

        self.THRESHOLD = 4500
        self.DEV_INDEX = False

    def save_speech(self, data, p):
        """
        Saves mic data to temporary WAV file. Returns filename of saved
        file
        """
        filename = 'output_'+str(int(time.time()))
        # writes data to WAV file
        data = ''.join(data)
        wf = wave.open(filename + '.wav', 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(16000)  # TODO make this value a function parameter?
        wf.writeframes(data)
        wf.close()
        return filename + '.wav'

    def decode_phrase(self, wav_file):
        stream = open(wav_file, "rb")

        #To turn off listening during decode:
        #stream.close()

        if self.keyword_detect:
            print "Looking for keyword"
            self.kw_decoder.start_utt()
            while True:
                buf = stream.read(1024)
                if buf:
                    self.kw_decoder.process_raw(buf, False, False)
                else:
                    self.kw_decoder.end_utt()
                    return []
                if self.kw_decoder.hyp() != None:
                    print ([(seg.word, seg.prob, seg.start_frame, seg.end_frame) for seg in self.kw_decoder.seg()])
                    print ("Detected keyword, restarting search")
                    self.kw_decoder.end_utt()

                    self.keyword_detect = False
                    return["keyword", "detected"]
        else:
            self.decoder.start_utt()
            self.kwoff_decoder.start_utt()
            while True:
                buf = stream.read(1024)
                if buf:
                    self.decoder.process_raw(buf, False, False)
                    self.kwoff_decoder.process_raw(buf, False, False)
                else:
                    self.decoder.end_utt()
                    self.kwoff_decoder.end_utt()
                    break
                if self.kwoff_decoder.hyp() != None:
                    print ([(seg.word, seg.prob, seg.start_frame, seg.end_frame) for seg in self.kwoff_decoder.seg()])
                    print ("Detected off keyword, restarting search")
                    self.decoder.end_utt()
                    self.kwoff_decoder.end_utt()

                    self.keyword_detect = True
                    return["off keyword", "detected"]
            #self.decoder.end_utt()
            #self.kwoff_config.end_utt()

            words = []
            [words.append(seg.word) for seg in self.decoder.seg()]
            return words


    def run(self):
        """
        Listens to Microphone, extracts phrases from it and calls pocketsphinx
        to decode the sound
        """
        #self.setup_mic()
        start = True

        #Open stream
        p = pyaudio.PyAudio()
        stream = p.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE, input=True, frames_per_buffer=self.CHUNK)
        print "* Mic set up and listening. "

        audio2send = []
        cur_data = ''  # current chunk of audio data
        rel = self.RATE/self.CHUNK
        slid_win = deque(maxlen=self.SILENCE_LIMIT * rel)
        #Prepend audio from 0.5 seconds before noise was detected
        prev_audio = deque(maxlen=self.PREV_AUDIO * rel)
        started = False

        #while not rospy.is_shutdown():
        #if self.detect == False:
        #    continue

        cur_data = stream.read(self.CHUNK)
        slid_win.append(math.sqrt(abs(audioop.avg(cur_data, 4))))

        if sum([x > self.THRESHOLD for x in slid_win]) > 0:
            if started == False: 
                print "Starting recording of phrase"
                #self.speech_status_pub.publish("LISTENING")
                started = True
            audio2send.append(cur_data)

        elif started:
            print "Finished recording, decoding phrase"
            start = False
            self.speech_status_pub.publish("DONE")
            filename = self.save_speech(list(prev_audio) + audio2send, p)
            #print "Actually Finished Recording."
            r = self.decode_phrase(filename)
            print "DETECTED: ", r
            speech_string = ""
            for word in r:
                if word[0] != "<":
                    speech_string += " " + word
            #if len(speech_string) > 0:
                #self.speech_pub.publish(speech_string)

            # Removes temp audio file
            os.remove(filename)
            # Reset all
            started = False
            slid_win = deque(maxlen=self.SILENCE_LIMIT * rel)
            prev_audio = deque(maxlen=0.5 * rel)
            audio2send = []
            print "Listening ..."

        else:
            prev_audio.append(cur_data)

        print "* Done listening"
        stream.close()
        p.terminate()

if __name__ == "__main__":
	sd = SpeechDetector()
	sd.run()