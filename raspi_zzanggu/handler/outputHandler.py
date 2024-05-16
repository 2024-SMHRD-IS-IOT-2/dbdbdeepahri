from common.thread import Thread, THREAD_STATUS
import os
import requests 
import time
import sounddevice as sd
import soundfile as sf

## typecast TTS 오디오 생성 쓰레드
## 인풋 큐 : flag, emotion, text
## 아웃풋 큐 : flag, emo, filename
class GenerateOutputAudioThread(Thread):
    def __init__(self, event, actor_id, api_key):
        super().__init__(target=self.target, event=event)
        self.ACTOR_ID = actor_id
        self.API_KEY = api_key
        self.cnt = 0

    ## 쓰레드 함수
    def target(self):
        while True:
            self.event.wait()
            if not self.input_queue.empty():
                flag, emo, text = self.input_queue.get_nowait()
                self.set_status(flag)
                if flag == THREAD_STATUS.FINISH:
                    self.push_output(flag, "", "")
                    break
                
                # 대화 종료시 파일카운터 초기화
                elif flag == THREAD_STATUS.DONE :
                    self.cnt = 0
                    print("sending Done")
                    self.push_output(flag, "", "")

                    self.event.clear() #대화생성쓰레드, tts쓰레드 대기모드로
                
                ## TTS 작업
                elif flag == THREAD_STATUS.RUNNING :
                    filename = f"./wav/ttsOut{self.cnt}.wav"
                    self.do_tts(text,filename,emo)
                    self.push_output(flag, emo, filename)
                    print("tts file created : ", filename)
                    self.cnt+=1
                     
    ## tts 처리함수
    def do_tts(self, text, filename, emotion='normal-1', lang='ko'):
        HEADERS = {'Authorization': f'Bearer {self.API_KEY}'}
        # request speech synthesis
        r = requests.post('https://typecast.ai/api/speak', headers=HEADERS, json={
            'text': text,
            'lang': lang,
            'actor_id': self.ACTOR_ID,
            'xapi_hd': True,
            'model_version': 'latest',
            "emotion_tone_preset": emotion
        })
        speak_url = r.json()['result']['speak_v2_url']
        
        # polling the speech synthesis result
        for _ in range(120):
            r = requests.get(speak_url, headers=HEADERS)
            ret = r.json()['result']
            # audio is ready
            if ret['status'] == 'done':
                # download audio file
                r = requests.get(ret['audio_download_url'])
                with open(filename, 'wb') as f:
                    f.write(r.content)
                break
            else :
                print("wait 0.1sec. processing tts")
                time.sleep(0.1)
                    

class PlayAudio:
    def __init__(self, queue):
        self.input_queue = queue

    # 인풋 큐 클리어 함수 (대화가 아닐 시)
    def clear_input(self):
        while not self.input_queue.empty():
            _, emo, filename = self.input_queue.get_nowait()
            os.remove(filename)

    def play_all_file(self):
        while True:
            if not self.input_queue.empty():
                flag, emo, filename = self.input_queue.get_nowait()
                if flag == THREAD_STATUS.FINISH:
                    break
                elif flag == THREAD_STATUS.DONE :
                    print("all audio played")
                    break
                
                elif flag == THREAD_STATUS.RUNNING :
                    data, fs = sf.read(filename, dtype='float32')  
                    time.sleep(0.3) ## 문장 사이사이 숨쉴 틈을..
                    # TODO : 아두이노 시리얼로 감정 보내기

                    print("play audio ", filename)
                    sd.play(data, fs)
                    status = sd.wait()  # Wait until file is done playing
                    os.remove(filename) # remove file after playing
                    time.sleep(0.3) ## 문장 사이사이 숨쉴 틈을..
                    



