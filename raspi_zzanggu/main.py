from handler.langchainHandler import TaskClassifier, ConvGenThread, TASK
from handler.outputHandler import GenerateOutputAudioThread, PlayAudioThread, PlayAudio
from handler.inputHandler import InputHandler
from model.emotionModel import EmotionModelThread
from threading import Event
from common.thread import THREAD_STATUS
import setup
from dotenv import load_dotenv
import os
import winsound as ws
import time
import sounddevice as sd
import soundfile as sf

def main():
    
    ## init
    event = Event()
    inputHandle = InputHandler(access_key=os.environ['PORCUPINE_ACCESS_KEY'],
                               keyword_file_path=os.environ['PORCUPINE_KEYWORD_FILE_PATH'],
                               model_file_path=os.environ['PORCUPINE_MODEL_FILE_PATH'],
                               sensitivity=float(os.environ['PORCUPINE_SENSITIVITY']))  
    taskClassifier = TaskClassifier(api_key=os.environ['OPENAI_API_KEY_CLASS'], temp=0.5, max_tokens=100)  ## 분류 llm 객체
    convGen = ConvGenThread(event, api_key=os.environ['OPENAI_API_KEY_CONV'], temp=1.2, max_tokens=100 )  ## 대화생성 llm 객체
    generateOutputAudio = GenerateOutputAudioThread(event=event,
                                                    actor_id=os.environ['TYPECAST_ACTOR_ID'], 
                                                    api_key=os.environ['TYPECAST_API_KEY']) ## 출력오디오 생성 객체
    # playAudio = PlayAudioThread(event)  ## 오디오 출력 객체
    playConvAudio = PlayAudio(generateOutputAudio.output_queue)
    # emotionModel = EmotionModelThread(event)
    
    convGen.set_output_queue(generateOutputAudio.input_queue)
    # generateOutputAudio.set_output_queue(playAudio.input_queue)

    convGen.start()
    # emotionModel.start()
    generateOutputAudio.start()
    # playAudio.start()
    isRunning = True
    event.clear()
    
    print("init done")

    # ## 메인
    while isRunning:
        

        ## 기존 대화 리셋
        convGen.reset_conversation()

        ## 키워드 인식 !! 완료 !!
        inputHandle.recognize_keyword()

        ## wakeup sound 
        ws.Beep(500, 500)
        ## TODO : 비프음 대신 대답파일로 교체. 
        ## TODO : arduino serial 신호 전송 (normal)
    

        ############### 대화 사이클
        while True :

            ## 유저 음성 받기 !! 완료 !!
            userInputIn, user_input_text, user_input_audio = inputHandle.get_user_input(filename='./wav/userSentence.wav',
                                                                                          inputWaitTIme=10, 
                                                                                          silence_duration=2, 
                                                                                          silence_threshold=40)
            
            ## 테스트 유저음성
            # userInputIn, user_input_text, user_input_audio = True, "넌 요즘 머하고 있니." , "./wav/userSentence.wav"
            
            ## 일정 시간동안 말 안했을떄. 아웃.
            if not userInputIn :
                ## TODO : arduino serial 신호 전송 (off / sleep)
                break
            
            ## 유저가 음성을 받았을 때
            else :
                # 백그라운드 쓰레드에서 감정분석, 대화생성(대답파일생성까지)
                # emotionModel.push_input(THREAD_STATUS.RUNNING, user_input_text, user_input_audio)
                
                event.set() ## 쓰레드 시작
                convGen.push_input(THREAD_STATUS.RUNNING, user_input_text)
                convGen.push_input(THREAD_STATUS.DONE, "")

                # 랭체인으로 음성 문자열 작업 분류
                task, arg = taskClassifier.classify(user_input_text) 

                ## 대화로 분류됐을 시 준비돼있는 오디오 출력
                if task == TASK.CONVERSATION:
                    print("task == conversation", arg)

                    ### 로직 변경 테스트
                    # 오디오를 non thread 로.
                    playConvAudio.play_all_file()
                    
                    print("conv done")

                elif task == TASK.MUSIC_RECOMMEND:
                    print("task == music recommendation", arg)
                    playConvAudio.clear_input()
                    # ! TODO music_file 재생
                    # playAudio.clear_input() # 오디오 클리어  
                    # while emotionModel.get_status() == THREAD_STATUS.RUNNING:
                    #     pass
                    # flag, music_file = emotionModel.output_queue.get_nowait()

                elif task == TASK.MUSIC_CTRL:
                    print("task == music control", arg)
                    playConvAudio.clear_input()
                    ## TODO : 음악 조정

                elif task == TASK.IOT_CTRL:
                    print("task == IoT Control", arg)
                    playConvAudio.clear_input()
                    
                            
            # break # TEST. 대화 사이클 while 종료
        
        print("exit conversation cycle")
    
        # break  # TEST. 메인 프로그램 loop 종료

    print("exit main loop")
    ## 대기중인 쓰레드 종료
    event.set()
    convGen.push_input(THREAD_STATUS.FINISH, "")
    convGen.finish()
    generateOutputAudio.finish()
    # # playAudio.finish()
    # # emotionModel.finish()
    print("thread all clear")


if __name__ == "__main__":
    ## install all requirements
    # setup.inst_all_from_requirements("requirements.txt")
    
    load_dotenv('./config/keys.env')
    
    main()

