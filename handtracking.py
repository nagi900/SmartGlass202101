import cv2
import mediapipe as mp
import time
import numpy as np
import math
from PIL import Image
from Lib.self_made import (
                        handsign_judge,
                        time_mesure,
                        drowing,
                        img_processing,
                            )

class HandTracking:
    def __init__(self):
        pass
    def run(self):#selfつけないと外から動かない
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

        ACTWIN_PXL_WIDTH=int(500) # 眼鏡に取り付けるディスプレイのウィンドウのピクセル数
        ACTWIN_PXL_HIGHT=int(500)
        ACTWIN_L_NAME='active window left' #ウィンドウの名前
        ACTWIN_R_NAME='active window right'
        LAYER_NUM = 4#レイヤーの枚数 最低4枚

        PUPILLARY_DISTANCE=60.0 #瞳と瞳の距離(PD)[mm]
        VERTEX_DISTANCE=12 #(角膜)頂点間距離{mm} 通常12mmくらい 角膜の頂点とレンズ後方の距離
        DISPLAY_WIDTH=100 #眼鏡に取り付けるディスプレイの横幅[mm]
        DISPLAY_HIGHT=100

        PALM_WIDTH=70 #人差し指の付け根の中心から小指の付け根の中心までの距離[mm]

        MAX_CAMERA_SIDE_ANGLE = math.pi/3 #カメラの横方向の画角[rad]
        MAX_CAMERA_VERTICAL_ANGLE = math.pi/3 #カメラの縦方向の画角[rad]

        cv2.namedWindow(ACTWIN_L_NAME) # これで一つwindowが開く　特に変数に代入したりする必要はない
        cv2.namedWindow(ACTWIN_R_NAME) 

        #左右のディスプレイに表示する真っ白の画像を生成
        WHITE_IMG = np.full((ACTWIN_PXL_WIDTH,ACTWIN_PXL_HIGHT,3),255)
        ALPHA_IMG = np.insert(WHITE_IMG,3,0,axis=2)
        WHITE_IMG = np.insert(WHITE_IMG,3,255,axis=2)#ここ普通に最初から全要素255にした方がいい
        IMG_LEFT_LAYER_PATH_0 = 'Image_layer/ImgLeft_0.png'
        IMG_RIGHT_LAYER_PATH_0 = 'Image_layer/ImgRight_0.png'
        cv2.imwrite(IMG_LEFT_LAYER_PATH_0,WHITE_IMG)
        cv2.imwrite(IMG_RIGHT_LAYER_PATH_0,WHITE_IMG)
        ImgLeft = cv2.imread(IMG_LEFT_LAYER_PATH_0,-1)#これをベースにしてレイヤーを合成する
        ImgRight = cv2.imread(IMG_RIGHT_LAYER_PATH_0,-1)#これをベースにする
        
        LeftLayers = [ImgLeft]
        RightLayers = [ImgRight]
        #合成するレイヤー
        for layer_num in range(LAYER_NUM-1):
            IMG_LEFT_LAYER_PATH = f'Image_layer/ImgLeft_{layer_num+1}.png'
            IMG_RIGHT_LAYER_PATH = f'Image_layer/ImgRight_{layer_num+1}.png'
            cv2.imwrite(IMG_LEFT_LAYER_PATH,ALPHA_IMG)
            cv2.imwrite(IMG_RIGHT_LAYER_PATH,ALPHA_IMG)
            ImgLeft = cv2.imread(IMG_LEFT_LAYER_PATH,-1)#-1をつけるとアルファチャンネルも読み込める
            ImgRight = cv2.imread(IMG_RIGHT_LAYER_PATH,-1)
            LeftLayers.append(ImgLeft)
            RightLayers.append(ImgRight)

        #合成して表示するかどうか(初期状態)
        wheather_merging_layer = [1]#ベースのImg_Left(もしくはRight)_layer_0は1
        for layer_num in range(LAYER_NUM-3):
            wheather_merging_layer.append(1)
        wheather_merging_layer.append(0)#後ろから2番目(modeを表示するレイヤー)は初期状態では非表示
        wheather_merging_layer.append(1)

        ins_jesture = handsign_judge.handsign_judge_1(PALM_WIDTH, (MAX_CAMERA_SIDE_ANGLE,MAX_CAMERA_VERTICAL_ANGLE))#先にこっち
        lefteye_process = img_processing.plr_trns(VERTEX_DISTANCE, (DISPLAY_WIDTH,DISPLAY_HIGHT) , (ACTWIN_PXL_WIDTH,ACTWIN_PXL_WIDTH), -PUPILLARY_DISTANCE/2)
        righteye_process = img_processing.plr_trns(VERTEX_DISTANCE, (DISPLAY_WIDTH,DISPLAY_HIGHT) , (ACTWIN_PXL_WIDTH,ACTWIN_PXL_WIDTH), PUPILLARY_DISTANCE/2)
        ins_drowing = drowing.drowing(LeftLayers, RightLayers, ins_jesture, lefteye_process, righteye_process, (ACTWIN_PXL_WIDTH,ACTWIN_PXL_WIDTH), wheather_merging_layer)#インスタンスも引き数にできる
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
                    mp_drawing.draw_landmarks( #これで画像に書き込んでる cv2を使っている
                        image, hand_landmarks, mp_hands.HAND_CONNECTIONS)


                    #オリジナル################################

                    #タプルhanc_landmarks内の辞書型landmarkを取得　
                    #辞書型を入れるにはタプル型の方が良い為　またパフォーマンスもタプル型の穂王が良い為
                    #詳細は調べる
                    for idx, landmark in enumerate(hand_landmarks.landmark):
                        # 番号とz座標を標準出力に表示 なんでlandmark[z]じゃダメなのか後で調べる
                        #print(idx,landmark.z)
                        
                        ins_jesture.setting(idx,landmark.x,landmark.y,landmark.z)
                    
                    #ここでprin t (ins_jesture.result())などとしてins_jestureを呼び出してしまうと
                    # 次のdrowing_3 D viewが反応しなくなってしまうのでやらな い 

                    ins_drowing.drowing_3Dview(ins_jesture.result(),"drowing_hand")#手のひらの表示をする場合は第二引き数に"drowing_hand"を


                    ##############################################

            
            #保存
            for layer_num in range(LAYER_NUM):
                cv2.imwrite(f'Image_layer/ImgLeft_{layer_num}.png',LeftLayers[layer_num])#merge後のlayer0の保存は一週遅れる
                cv2.imwrite(f'Image_layer/ImgRight_{layer_num}.png',RightLayers[layer_num])
            #合成 drowing内でやった方がいいかも
            bg_L = Image.open(IMG_LEFT_LAYER_PATH_0).convert("RGBA")
            bg_R = Image.open(IMG_RIGHT_LAYER_PATH_0).convert("RGBA")
            for layer_num in range(LAYER_NUM-1):
                if ins_drowing.wheather_merging_layer[layer_num+1]:#whether_mergingが9でないなら
                    img_L = Image.open(f'Image_layer/ImgLeft_{layer_num+1}.png').convert("RGBA")
                    img_R = Image.open(f'Image_layer/ImgRight_{layer_num+1}.png').convert("RGBA")
                    bg_L = Image.alpha_composite(bg_L,img_L)
                    bg_R = Image.alpha_composite(bg_R,img_R)
            bg_L.save('Image_layer/ImgLeft_0.png')
            bg_R.save('Image_layer/ImgRight_0.png')
            #for文を使わないで、縦に羅列した方がfpsが早かった気がする

            #表示
            Left = cv2.imread(IMG_LEFT_LAYER_PATH_0)#同じインスタンス名で読み込むと画像が重なってしまう
            Right = cv2.imread(IMG_RIGHT_LAYER_PATH_0)
            cv2.imshow(ACTWIN_L_NAME,Left)
            cv2.imshow(ACTWIN_R_NAME,Right)
            cv2.imshow('MediaPipe Hands', image)
            #
            if cv2.waitKey(5) & 0xFF == 27:
                break
        hands.close()
        cap.release()

        #out.release()#オリジナル　録画

if __name__=="__main__":
    HandTracking().run()