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

class Handtracking:
    def __init__(self):
        super().__init__()
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_hands = mp.solutions.hands

        # For webcam input:
        self.hands = self.mp_hands.Hands(
            min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.cap = cv2.VideoCapture(0)


        #オリジナル#########################

        self.font = cv2.FONT_HERSHEY_SIMPLEX #fontのところを元のまま書くと、cv2.FONT~ の.に反応してしまう

        ##カメラ映像を録画　フレームレートが合わないので直さないといけない
        #fourcc=cv2.VideoWriter_fourcc(*'mp4v') # 書き出すコーデック名
        #out=cv2.VideoWriter('output.mp4',fourcc, 8.0, (640,480))#書き込むファイル 謎 フレームレート 縦横比？

        self.ACTWIN_PXL_WIDTH=int(500) # 眼鏡に取り付けるディスプレイのウィンドウのピクセル数
        self.ACTWIN_PXL_HIGHT=int(500)
        self.ACTWIN_L_NAME='active window left' #ウィンドウの名前
        self.ACTWIN_R_NAME='active window right'
        self.LAYER_NUM = 5#レイヤーの枚数 最低5枚 LAYER_NUM-4が表示できるobjectのレイヤー数

        self.PUPILLARY_DISTANCE=60.0 #瞳と瞳の距離(PD)[mm]
        self.VERTEX_DISTANCE=12 #(角膜)頂点間距離{mm} 通常12mmくらい 角膜の頂点とレンズ後方の距離
        self.DISPLAY_WIDTH=100 #眼鏡に取り付けるディスプレイの横幅[mm]
        self.DISPLAY_HIGHT=100

        self.PALM_WIDTH=70 #人差し指の付け根の中心から小指の付け根の中心までの距離[mm]

        self.MAX_CAMERA_SIDE_ANGLE = math.pi/3 #カメラの横方向の画角[rad]
        self.MAX_CAMERA_VERTICAL_ANGLE = math.pi/3 #カメラの縦方向の画角[rad]

        
        if __name__=="__main__":
            cv2.namedWindow(self.ACTWIN_L_NAME) # これで一つwindowが開く　特に変数に代入したりする必要はない
            cv2.namedWindow(self.ACTWIN_R_NAME) 

        #左右のディスプレイに表示する真っ白の画像を生成
        self.WHITE_IMG = np.full((self.ACTWIN_PXL_WIDTH,self.ACTWIN_PXL_HIGHT,3),255)
        self.ALPHA_IMG = np.insert(self.WHITE_IMG,3,0,axis=2)
        self.WHITE_IMG = np.insert(self.WHITE_IMG,3,255,axis=2)#ここ普通に最初から全要素255にした方がいい
        self.IMG_LEFT_LAYER_PATH_0 = 'Image_layer/ImgLeft_0.png'
        self.IMG_RIGHT_LAYER_PATH_0 = 'Image_layer/ImgRight_0.png'
        cv2.imwrite(self.IMG_LEFT_LAYER_PATH_0,self.WHITE_IMG)
        cv2.imwrite(self.IMG_RIGHT_LAYER_PATH_0,self.WHITE_IMG)
        self.ImgLeft = cv2.imread(self.IMG_LEFT_LAYER_PATH_0,-1)#これをベースにしてレイヤーを合成する
        self.ImgRight = cv2.imread(self.IMG_RIGHT_LAYER_PATH_0,-1)#これをベースにする
        
        self.LeftLayers = [self.ImgLeft]
        self.RightLayers = [self.ImgRight]
        #合成するレイヤー
        for layer_num in range(self.LAYER_NUM-1):
            img_left_layer_path = f'Image_layer/ImgLeft_{layer_num+1}.png'
            img_right_layer_path = f'Image_layer/ImgRight_{layer_num+1}.png'
            cv2.imwrite(img_left_layer_path,self.ALPHA_IMG)
            cv2.imwrite(img_right_layer_path,self.ALPHA_IMG)
            ImgLeft = cv2.imread(img_left_layer_path,-1)#-1をつけるとアルファチャンネルも読み込める
            ImgRight = cv2.imread(img_right_layer_path,-1)
            self.LeftLayers.append(ImgLeft)
            self.RightLayers.append(ImgRight)

        #合成して表示するかどうか(初期状態)
        self.wheather_merging_layer = [1]#ベースのImg_Left(もしくはRight)_layer_0は1
        for layer_num in range(self.LAYER_NUM-3):
            self.wheather_merging_layer.append(1)
        self.wheather_merging_layer.append(0)#後ろから2番目(modeを表示するレイヤー)は初期状態では非表示
        self.wheather_merging_layer.append(1)

        self.ins_jesture = handsign_judge.handsign_judge_1(self.PALM_WIDTH, (self.MAX_CAMERA_SIDE_ANGLE, self.MAX_CAMERA_VERTICAL_ANGLE))#先にこっち
        self.lefteye_process = img_processing.plr_trns(self.VERTEX_DISTANCE, (self.DISPLAY_WIDTH,self.DISPLAY_HIGHT) , (self.ACTWIN_PXL_WIDTH, self.ACTWIN_PXL_WIDTH), -self.PUPILLARY_DISTANCE/2)
        self.righteye_process = img_processing.plr_trns(self.VERTEX_DISTANCE, (self.DISPLAY_WIDTH,self.DISPLAY_HIGHT) , (self.ACTWIN_PXL_WIDTH, self.ACTWIN_PXL_WIDTH), self.PUPILLARY_DISTANCE/2)
        self.ins_drowing = drowing.drowing(self.LeftLayers, self.RightLayers, self.ins_jesture, self.lefteye_process, self.righteye_process, (self.ACTWIN_PXL_WIDTH, self.ACTWIN_PXL_WIDTH), self.wheather_merging_layer)#インスタンスも引き数にできる
        ########################################


    def run(self):#selfつけないと外から動かない
        while self.cap.isOpened():
            success, image = self.cap.read()
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
            results = self.hands.process(image)  
            # Draw the hand annotations on the image.
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            
            if results.multi_hand_landmarks:
                
                for hand_landmarks in results.multi_hand_landmarks:
                    self.mp_drawing.draw_landmarks( #これで画像に書き込んでる cv2を使っている
                        image, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)


                    #オリジナル################################

                    #タプルhanc_landmarks内の辞書型landmarkを取得　
                    #辞書型を入れるにはタプル型の方が良い為　またパフォーマンスもタプル型の穂王が良い為
                    #詳細は調べる
                    for idx, landmark in enumerate(hand_landmarks.landmark):
                        # 番号とz座標を標準出力に表示 なんでlandmark[z]じゃダメなのか後で調べる
                        #print(idx,landmark.z)
                        
                        self.ins_jesture.setting(idx,landmark.x,landmark.y,landmark.z)
                    
                    #ここでprin t (ins_jesture.result())などとしてins_jestureを呼び出してしまうと
                    # 次のdrowing_3 D viewが反応しなくなってしまうのでやらな い 

                    self.ins_drowing.drowing_3Dview(self.ins_jesture.result(),"drowing_hand")#手のひらの表示をする場合は第二引き数に"drowing_hand"を


                    ##############################################

            
            #保存
            for layer_num in range(self.LAYER_NUM):
                cv2.imwrite(f'Image_layer/ImgLeft_{layer_num}.png',self.LeftLayers[layer_num])#merge後のlayer0の保存は一週遅れる
                cv2.imwrite(f'Image_layer/ImgRight_{layer_num}.png',self.RightLayers[layer_num])
            #合成 drowing内でやった方がいいかも
            bg_L = Image.open(self.IMG_LEFT_LAYER_PATH_0).convert("RGBA")
            bg_R = Image.open(self.IMG_RIGHT_LAYER_PATH_0).convert("RGBA")
            for layer_num in range(self.LAYER_NUM-1):
                if self.ins_drowing.wheather_merging_layer[layer_num+1]:#whether_mergingが9でないなら
                    img_L = Image.open(f'Image_layer/ImgLeft_{layer_num+1}.png').convert("RGBA")
                    img_R = Image.open(f'Image_layer/ImgRight_{layer_num+1}.png').convert("RGBA")
                    bg_L = Image.alpha_composite(bg_L,img_L)
                    bg_R = Image.alpha_composite(bg_R,img_R)
            bg_L.save('Image_layer/ImgLeft_0.png')
            bg_R.save('Image_layer/ImgRight_0.png')
            #for文を使わないで、縦に羅列した方がfpsが早かった気がする

            #表示
            Left = cv2.imread(self.IMG_LEFT_LAYER_PATH_0)#同じインスタンス名で読み込むと画像が重なってしまう
            Right = cv2.imread(self.IMG_RIGHT_LAYER_PATH_0)
            if __name__=="__main__":
                cv2.imshow(self.ACTWIN_L_NAME,Left)
                cv2.imshow(self.ACTWIN_R_NAME,Right)
                cv2.imshow('MediaPipe Hands', image)
            #
            if cv2.waitKey(5) & 0xFF == 27  or not __name__=="__main__":#外部から実行されていても一周で終わる
                break
        self.hands.close()
        self.cap.release()

        #out.release()#オリジナル　録画

if __name__=="__main__":
    Handtracking().run()