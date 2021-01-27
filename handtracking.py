import cv2
import mediapipe as mp
import time
import numpy as np
import math
from Lib.self_made import (
                        handsign_judge,
                        time_mesure,
                        drowing,
                        img_processing,
                            )

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# For webcam input:
hands = mp_hands.Hands(
    min_detection_confidence=0.5, min_tracking_confidence=0.5)
cap = cv2.VideoCapture(0)


#オリジナル#########################

font = cv2.FONT_HERSHEY_SIMPLEX #fontのところを元のまま書くと、cv2.FONT~ の.に反応してしまう

##カメラ映像を録画　フレームレートが合わないので直さないといけない
#fourcc=cv2.VideoWriter_fourcc(*'mp4v') # 書き出すコーデック名
#out=cv2.VideoWriter('output.mp4',fourcc, 8.0, (640,480))#書き込むファイル 謎 フレームレート 縦横比？

actwin_width=int(500) # 目に表示するウィンドウの大きさ
actwin_height=int(500)
ACTWIN_L_NAME='active window left' #ウィンドウの名前
ACTWIN_R_NAME='active window right'

PUPILLARY_DISTANCE=60.0 #瞳と瞳の距離(PD)[mm]
VERTEX_DISTANCE=12 #(角膜)頂点間距離{mm} 通常12mmくらい 角膜の頂点とレンズ後方の距離
DISPLAY_WIDTH=100 #眼鏡に取り付けるディスプレイの横幅[mm]
#CAMERA_DISTANCE=150 #左右のカメラの距離[mm]

PALM_WIDTH=70 #人差し指の付け根の中心から小指の付け根の中心までの距離[mm]

MAX_CAMERA_SIDE_ANGLE = math.pi/3 #カメラの横方向の画角[rad]
MAX_CAMERA_VERTICAL_ANGLE = math.pi/3 #カメラの縦方向の画角[rad]

cv2.namedWindow(ACTWIN_L_NAME) # これで一つwindowが開く　特に変数に代入したりする必要はない
cv2.namedWindow(ACTWIN_R_NAME) 

#左右のディスプレイに表示する真っ白の画像を生成
WHITE_IMG = np.full((actwin_height,actwin_width,3),255)
IMG_LEFT_NAME = 'ImgLeft.png'
IMG_RIGHT_NAME = 'ImgRight.png'
cv2.imwrite(IMG_LEFT_NAME,WHITE_IMG)
cv2.imwrite(IMG_RIGHT_NAME,WHITE_IMG)
ImgLeft = cv2.imread(IMG_LEFT_NAME)
ImgRight = cv2.imread(IMG_RIGHT_NAME)
#ここにアクティブウィンドウのスクショの画像を表示するやつを書く

hoge1=handsign_judge.handsign_judge_1(PALM_WIDTH,MAX_CAMERA_SIDE_ANGLE,MAX_CAMERA_VERTICAL_ANGLE)#先にこっち
lefteye_process=img_processing.plr_trns(VERTEX_DISTANCE,DISPLAY_WIDTH,-PUPILLARY_DISTANCE/2)
righteye_process=img_processing.plr_trns(VERTEX_DISTANCE,DISPLAY_WIDTH,PUPILLARY_DISTANCE/2)
hoge2=drowing.drowing(ImgLeft,ImgRight,hoge1,lefteye_process,righteye_process)#インスタンスも引き数にできる
########################################


while cap.isOpened():
    success, image = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        # If loading a video, use 'break' instead of 'continue'.
        continue  
    # Flip the image horizontally for a later selfie-view display, and convert
    # the BGR image to RGB.
    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
    # To improve performance, optionally mark the image as not writeable to
    # pass by reference.
    image.flags.writeable = False
    results = hands.process(image)  
    # Draw the hand annotations on the image.
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    
    if results.multi_hand_landmarks:
        
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks( #これで画像に書き込んでる
                image, hand_landmarks, mp_hands.HAND_CONNECTIONS)


            #オリジナル################################

            #タプルhanc_landmarks内の辞書型landmarkを取得　
            #辞書型を入れるにはタプル型の方が良い為　またパフォーマンスもタプル型の穂王が良い為
            #詳細は調べる
            for idx, landmark in enumerate(hand_landmarks.landmark):
                # 番号とz座標を標準出力に表示 なんでlandmark[z]じゃダメなのか後で調べる
                #print(idx,landmark.z)
                
                hoge1.setting(idx,landmark.x,landmark.y,landmark.z)
            
            #ここでprint(hoge1.result())などとしてhoge1を呼び出してしまうと
            # 次のdrowing_3Dviewが反応しなくなってしまうのでやらない

            #↓defaultの黒い画面になってしまう
            #cv2.imwrite(IMG_LEFT_NAME,WHITE_IMG)
            #cv2.imwrite(IMG_RIGHT_NAME,WHITE_IMG)
            #ImgLeft = cv2.imread(IMG_LEFT_NAME)
            #ImgRight = cv2.imread(IMG_RIGHT_NAME)
            hoge2.drowing_3Dview(hoge1.result())


            ##############################################

    
    cv2.imshow('MediaPipe Hands', image)
    cv2.imshow(ACTWIN_L_NAME,ImgLeft) #winname(ここではACTWIN_L_NAME)にmat(ここではImgLeft)を表示
    cv2.imshow(ACTWIN_R_NAME,ImgRight)
    #↓defaultの黒い画面になってしまう
    #cv2.imwrite(IMG_LEFT_NAME,WHITE_IMG)
    #cv2.imwrite(IMG_RIGHT_NAME,WHITE_IMG)
    #ImgLeft = cv2.imread(IMG_LEFT_NAME)
    #ImgRight = cv2.imread(IMG_RIGHT_NAME)
    if cv2.waitKey(5) & 0xFF == 27:
        break
hands.close()
cap.release()

#out.release()#オリジナル　録画