#!/usr/bin/env python3

# Copyright (c) 2018 Anki, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License in the file LICENSE.txt or at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License isvi distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Play audio files through Vector's speaker.
"""
import os
import sys
import threading
import time
import anki_vector
from anki_vector.util import degrees
from PIL import Image

import soundfile as sf
#from pydub import AudioSegment

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("Cannot import from PIL. Do `pip3 install --user Pillow` to install")

# Get font file from computer (change directory as needed)
try:
    font_file = ImageFont.truetype("arial.ttf", 20)
except IOError:
    try:
        font_file = ImageFont.truetype(
            "/usr/share/fonts/noto/NotoSans-Medium.ttf", 20)
    except IOError:
        pass


def make_text_image(text_to_draw, x, y, font=None):
    dimensions = (184, 96)
    # make a blank image for the text, initialized to opaque black
    text_image = Image.new('RGBA', dimensions, (0, 0, 0, 255))
    # get a drawing context
    dc = ImageDraw.Draw(text_image)
    # draw the text
    dc.text((x, y), text_to_draw, fill=(255, 255, 255, 255), font=font)
    return text_image


def cube_keep_connect():
    global robot, connected_cube
    global stop_var #루프 탈출 변수

    stop_var = False
    timer_var = 0

    while True:
        time.sleep(5)
        timer_var += 5

        if timer_var % 15 == 0:
            max_attempts = 5
            attempts = 0
            while attempts < max_attempts:
                try:
                    #print("2. connect to a cube...")
                    robot.world.connect_cube()
                    attempts = attempts + 1
                    connected_cube = robot.world.connected_light_cube
                    if connected_cube:
                        #print("2. done connecting!")
                        connected_cube.set_light_corners(anki_vector.lights.blue_light,
                                                         anki_vector.lights.off_light,
                                                         anki_vector.lights.red_light,
                                                         anki_vector.lights.off_light)
                    break
                except:
                    print("-Exception!!")
                    break

        if stop_var:
            break



def cube():
    global robot, connected_cube

    max_attempts = 5
    attempts = 0
    while attempts < max_attempts:
        print("connect to a cube...")

        robot.world.connect_cube()
        attempts = attempts + 1
        connected_cube = robot.world.connected_light_cube
        if connected_cube:
            print("done connecting!")
            connected_cube.set_light_corners(anki_vector.lights.blue_light,
                                             anki_vector.lights.off_light,
                                             anki_vector.lights.red_light,
                                             anki_vector.lights.off_light)
            break



def effect_wav():
    global robot

    volume = 45
    play_wav = "effect.wav"

    try:
        robot.audio.stream_wav_file(play_wav, volume)
    except anki_vector.exceptions.VectorExternalAudioPlaybackException:
        # print("다시")
        mythread = threading.Thread(target=effect_wav)
        mythread.start()


def wav():
    global robot
    global the_song_end, anki_wav_file_list

    the_song_end = False#음악이 끝까지 재생되고 다음 음아긍로 넘어갈 변수
    volume = 40

    play_wav = anki_wav_file_list[i]

    # sound = AudioSegment.from_wav(play_wav)
    # print(sound.frame_rate)
    # if sound.frame_rate > 16000 or sound.channels > 1:
    #     sound = sound.set_channels(1)
    #     sound = sound.set_frame_rate(16000)
    #     sound.export(play_wav, format="wav")
    #     print("음악포맷")

    try:
        robot.audio.stream_wav_file(play_wav, volume)
        the_song_end = True
        print(">> the song end")
    except anki_vector.exceptions.VectorExternalAudioPlaybackException:
        #print("다시")
        mythread = threading.Thread(target=wav)
        mythread.start()

    # finally:
    #     if anki_vector.audio.playback_error is not None:
    #         anki_vector.audio.playback_error = None
    #         mythread = threading.Thread(target=wav)
    #         mythread.start()



def photo():
    global robot, connected_cube
    global the_song_end, anki_wav_file_list
    global n, i

    n = 0  # 루프 끝내기 용
    next_song = True #벡터를 들었을때 다음/이전 곡으로 넘어갈 변수

    robot.behavior.set_head_angle(anki_vector.behavior.MAX_HEAD_ANGLE)  # 고개를 들라
    robot.behavior.set_lift_height(0.0)

    robot.behavior.say_text("Select  the  Music!")
    time.sleep(0.7)

    effect_wav_thread = threading.Thread(target=effect_wav)
    effect_wav_thread.start()

    next_select = True
    while True:
        robot.screen.set_screen_with_image_data(anki_image_file_list[i], 0.28)
        if connected_cube:
            if connected_cube.up_axis == 1:  # 왼쪽 (블루)
                if next_select:
                    effect_wav_thread = threading.Thread(target=effect_wav)
                    effect_wav_thread.start()
                    next_select = False
                    i -= 1
                    if (i + 1) == 0:
                        i = len(anki_image_file_list) - 1
                    print(">> before music")
            elif connected_cube.up_axis == 2:  # 오른쪽 (레드)
                if next_select:
                    effect_wav_thread = threading.Thread(target=effect_wav)
                    effect_wav_thread.start()
                    next_select = False
                    i += 1
                    if i >= len(anki_image_file_list):
                        i = 0
                    print(">> next music")
            elif connected_cube.up_axis == 4 or connected_cube.up_axis == 3:
                break
            else:
                next_select = True

        time.sleep(0.2)




    while True:
        if n == 1:
            print("break")
            break

        robot.behavior.set_head_angle(anki_vector.behavior.MAX_HEAD_ANGLE)  # 고개를 들라
        robot.behavior.set_lift_height(0.0)

        try:
            f = sf.SoundFile(anki_wav_file_list[i])
            sec = len(f) / f.samplerate #노래 길이 구하기
        except:
            print("There is no .wav file...")
            text_to_draw = "       No wav file\n\n Check songs folder"
            face_image = make_text_image(text_to_draw, 0, 14, font_file)
            screen_data = anki_vector.screen.convert_image_to_screen_data(face_image)
            robot.screen.set_screen_with_image_data(screen_data, 2.5, interrupt_running=True)
            robot.behavior.say_text("there is no wav file")

            time.sleep(1)
            i += 1
            if i >= len(anki_image_file_list):
                i = 0
            continue


        print(">> Play MP3...")
        print('>> Song duration = {}sec'.format(round(sec, 0)))
        wav_thread = threading.Thread(target=wav)  # 음악 비동기 재생
        wav_thread.start()
        robot.screen.set_screen_with_image_data(anki_image_file_list[i], sec)  # 벡터 화면 재생

        while True:
            current_accel = robot.accel
            accel = str(current_accel).split(" ")
            #accel_x = float(accel[2])
            accel_y = float(accel[4])
            #accel_z = float(accel[6][:-1])
            accel_y_f = round(accel_y * 0.01, 1)

            is_being_touched = robot.touch.last_sensor_reading.is_being_touched

            if connected_cube: #큐브가 연결 상태라면
                if connected_cube.up_axis == 1: # 왼쪽(파랑)
                    if next_song:
                        next_song = False
                        i -= 2
                        if (i + 2) == 0:
                            i = len(anki_image_file_list) - 1 - 1
                        print(">> Previous song..")
                        break
                elif connected_cube.up_axis == 2: # 오른쪽(빨강)
                    if next_song:
                        print(">> next song..")
                        next_song = False
                        break
                elif connected_cube.up_axis == 5: # 큐브 뒤집기 노래 선택
                    n=1
                    
                    pause_thread = threading.Thread(target=stop, args={})
                    pause_thread.start()
                    break
                else:
                    next_song = True
                    if the_song_end:
                        the_song_end = False
                        print(">> next song..")
                        break

            if accel_y_f < -36.0:
                if next_song:
                    print(">> next song..")
                    next_song = False
                    break

            elif accel_y_f > 36.0:
                if next_song:
                    next_song = False
                    i-=2
                    if (i+2) == 0:
                        i = len(anki_image_file_list) -1 -1
                    print(">> Previous song..")
                    break
            else:
                next_song = True
                if the_song_end:
                    the_song_end = False
                    print(">> next song..")
                    break

            if is_being_touched:#벡터 만지면
                n=1
                mythread3 = threading.Thread(target=exitt, args={})  # 프로그램 종료
                mythread3.start()
                #exitt()
                break

            time.sleep(0.2)

        if n == 0:
            robot.disconnect()
            args = anki_vector.util.parse_command_args()
            robot = anki_vector.Robot(args.serial)
            robot.connect()
            mythread2 = threading.Thread(target=cube, args={})  # 큐브연결
            mythread2.start()

            if i >= len(anki_image_file_list) - 1:
                i = 0
            else:
                i += 1

        image_file = Image.open("logo.jpg")
        resize_image = image_file.resize((184, 96), Image.BICUBIC)
        screen_data = anki_vector.screen.convert_image_to_screen_data(resize_image)
        robot.screen.set_screen_with_image_data(screen_data, 1.0)  # 벡터 화면 재생




def stop():
    global robot

    robot.disconnect()
    args = anki_vector.util.parse_command_args()
    robot = anki_vector.Robot(args.serial)
    robot.connect()

    image_file = Image.open("logo.jpg")
    resize_image = image_file.resize((184, 96), Image.BICUBIC)
    screen_data = anki_vector.screen.convert_image_to_screen_data(resize_image)
    robot.screen.set_screen_with_image_data(screen_data, 3.0)  # 벡터 화면 재생

    mythread = threading.Thread(target=cube, args={})  # 큐브연결
    mythread.start()

    photo()

def exitt():
    global robot
    global stop_var

    stop_var = True
    robot.world.disconnect_cube()
    robot.disconnect()
    sys.exit()


def version_say():
    global robot

    robot.behavior.set_head_angle(anki_vector.behavior.MAX_HEAD_ANGLE)  # 고개를 들라
    robot.behavior.set_lift_height(0.0)

    image_file = Image.open("logo.jpg")
    resize_image = image_file.resize((184, 96), Image.BICUBIC)
    screen_data = anki_vector.screen.convert_image_to_screen_data(resize_image)
    robot.screen.set_screen_with_image_data(screen_data, 6.5)  # 벡터 화면 재생
    print("Vector MP3 Player. ver 2.0")
    robot.behavior.say_text("Vector MP3 Player version 2!")

def run():
    global robot, connected_cube
    global anki_image_file_list, anki_wav_file_list
    global i

    i = 0  # 리스트 인덱스 용
    connected_cube = False

    args = anki_vector.util.parse_command_args()
    robot = anki_vector.Robot(args.serial)
    robot.connect()

    # robot.conn.request_control(
    #      behavior_control_level=anki_vector.connection.ControlPriorityLevel.OVERRIDE_BEHAVIORS_PRIORITY)

    mythread3 = threading.Thread(target=version_say)
    mythread3.start()

    robot.world.disconnect_cube()
    time.sleep(1.2)
    mythread = threading.Thread(target=cube)
    mythread.start()
    mythread2 = threading.Thread(target=cube_keep_connect)
    mythread2.start()


    filename = "MP3_List.txt"
    inList = list()

    if not os.path.isfile(filename):  # path경로에서 파일 잇는지 검사
        # 파일이 없으면..
        print("Please Create :( 'MP3_List.txt' file")
    else:
        # 파일이 있으면..
        with open(filename, "r", encoding='utf-8-sig') as inFp:
            #inList = inFp.readlines()
            inList_tmp = inFp.read().splitlines()
            for txt in inList_tmp:
                if txt:
                    inList.append(txt)
            print(inList)

    anki_image_file_list = []#화면사진 재생 리스트
    anki_wav_file_list_temp = []
    for name in inList:  # 안키 벡터용 이미지로 변환하여 리스트로 저장
        try:
            image_file = Image.open("face_images\\" + name + ".jpg")
            resize_image = image_file.resize((184, 96), Image.BICUBIC)
            screen_data = anki_vector.screen.convert_image_to_screen_data(resize_image)
            anki_image_file_list.append(screen_data)
            anki_wav_file_list_temp.append(name) #그림 파일이 있으면 추가. 그림과 노래 일치를 위해서..
            #기본적으로 노래 리스트는 이미지 리스트를 이용해서 저장됨. 그림 = 노래 일치를 위해서..
            #그림만 딸랑 있으면 넘어가지만, 노래만 딸랑 있을경우 상관없음. 애초에 무시됨. 메인이 그림 파일이라서..
        except:
            print("Ignore file - face_images\\" + name + ".jpg")
            continue

    anki_wav_file_list = []#wav 재생 리스트
    for name in anki_wav_file_list_temp:  # 안키 벡터용 이미지로 변환하여 리스트로 저장
        anki_wav_file_list.append("songs\\" + name + ".wav")

    time.sleep(2.2)
    photo()
    # evt=threading.Event()
    # robot.events.subscribe(change, anki_vector.events.Events.audio_send_mode_changed, evt)



if __name__ == "__main__":
    run()

