import numpy as np
import math
from Lib.self_made import time_mesure

class handsignJudgeClass:
    def __init__(self,palm_width,max_angle,time_mesure_ins):
        self.palm_width=palm_width#手のひらの横幅
        self.halfof_palm_width = palm_width / 2 #手のひらの横幅の半分
        self.MHA = max_angle[0] #max_horaizontal_angle横方向の画角
        self.MVA = max_angle[1] #max_vertical_angle縦方向の画角
        self.tm = time_mesure_ins

        self.landmarks = {}
        self.landmark_x=0.0
        self.landmark_y=0.0
        self.landmark_z=0.0

        self.palm_direction_info="a"##手のひらの裏表を判別　palm_directionで使用

        self.middlefingure_vector_x=0.0
        self.middlefingure_vector_y=0.0
        self.middlefingure_vector_z=0.0
        self.middlefingure_vector_1ofabs=0.0
        self.middlefingure_vector=[]

        #finger_raising
        self.FingerRaising_value = 0.0
        self.x_n=0.0 
        self.x_a=0.0 
        self.x_q=0.0 
        self.y_n=0.0 
        self.y_a=0.0 
        self.y_q=0.0
        self.y_n=0.0 
        self.y_a=0.0 
        self.y_q=0.0 
        self.FingerRaising_info = {}

        #absdis_3D
        self.abdis3D_result = float()

        #absdis_2D
        self.abdis2D_result = float()

        #palm_dipth
        self.palm_dipth_info=0.0

        #rect_trans
        self.rectTransMagn = None
        self.rectTrans_result = []
        
        #keyboard_typing
        self.fingerVec = []

        #handSingText
        self.handSingText_result="noSign"
        self.handSingText_result_backup="noSign"

    #まずこれを呼び出して設定
    def setting(self,idx,landmark_x,landmark_y,landmark_z):#landmark):#
        self.idx=idx
        #self.landmark=landmark
        self.landmark_x = -landmark_x+0.5 #カメラ映像中央をx=0とする 画面が鏡写しなので、値を反転
        self.landmark_y = -(landmark_y-0.5) * self.MHA/self.MVA
        #カメラ映像中央をy=0とし、縦方向角度と単位をそろえる 下向きがyだったので、反転して上向きをyに
        self.landmark_z = landmark_z
        this_idx_position=[self.landmark_x,self.landmark_y,self.landmark_z]
        
        self.landmarks[self.idx] = this_idx_position #self.landmark

    #手のひらの裏表を判別
    def palm_direction(self):#向きdirection
        if np.abs(self.landmarks[5][0]-self.landmarks[17][0]) > np.abs(self.landmarks[0][2]-self.landmarks[9][2])/3:#手のひらの縦幅(カメラ映像上)の1/3以上差があるなら
            if self.landmarks[5][0]-self.landmarks[17][0] < 0:#右手で人差し指の付け根が小指の付け根より左にあるなら
                self.palm_direction_info = "reverse"
            else :
                self.palm_direction_info = "overse"
        else:
            self.palm_direction_info = "sidewayspalm"
        return self.palm_direction_info

    #中指の付け根のの向きを判別
    def midfin_vec(self):
        self.middlefingure_vector_x=self.landmarks[9][0] - self.landmarks[0][0]
        self.middlefingure_vector_y=self.landmarks[9][1] - self.landmarks[0][1]
        self.middlefingure_vector_z=self.landmarks[9][2] - self.landmarks[0][2]
        #(1/ベクトルの絶対値)を求める
        self.middlefingure_vector_1ofabs = 1 / self.abdis_3D(9,0)
        #各ベクトルに(1/ベクトルの絶対値)を掛ける
        self.middlefingure_vector_info =  [
                self.middlefingure_vector_1ofabs*self.middlefingure_vector_x,
                self.middlefingure_vector_1ofabs*self.middlefingure_vector_y,
                self.middlefingure_vector_1ofabs*self.middlefingure_vector_z
        ]
        return self.middlefingure_vector_info

    def FingerRaising(self):
        #法線ベクトルn(x_n,y_n,z_n) の 点A(x_a,y_a,z_a) を含む面S
        #任意の面上の点P(x_p,y_p,z_p) を考える
        #APとnは垂直 ∴AP・n=0 
        #空間内の任意の点Q(x_q,y_q,z_q) を考えると　AQ・n>0なら面Sよりnベクトル方向に正
        for i in range(5,18,4):
            self.x_n,self.y_n,self.z_n=self.midfin_vec()
            self.x_a=self.landmarks[i][0]
            self.x_q=self.landmarks[i+3][0]
            self.y_a=self.landmarks[i][1]
            self.y_q=self.landmarks[i+3][1]
            self.z_a=self.landmarks[i][2]
            self.z_q=self.landmarks[i+3][2]
            self.FingerRaising_value = (
                self.x_n*(self.x_q-self.x_a)+
                self.y_n*(self.y_q-self.y_a)+
                self.z_n*(self.z_q-self.z_a)
                )
            #キーを付け根の番号にしてFingerRaising_infoに指の曲げ伸ばしを代入
            if self.FingerRaising_value - self.abdis_3D(9,0)/2 >= 0:
                self.FingerRaising_info[str(i)] = 1
            #手のひらの縦の長さの1/3>付け根との差>0 の範囲内なら
            elif self.FingerRaising_value > 0:
                self.FingerRaising_info[str(i)] = 0
            else :
                self.FingerRaising_info[str(i)] = -1
        return self.FingerRaising_info

    def abdis_3D(self,abdis3D_mknum1,abdis3D_mknum2):#absolute distance 3D 2点間のx,y,z方向の絶対値
        
        self.abdis3D_result = math.sqrt(
            ((self.landmarks[abdis3D_mknum1][0] - self.landmarks[abdis3D_mknum2][0]))**2 +
            ((self.landmarks[abdis3D_mknum1][1] - self.landmarks[abdis3D_mknum2][1]))**2 +
            ((self.landmarks[abdis3D_mknum1][2] - self.landmarks[abdis3D_mknum2][2]))**2 
        )
        return self.abdis3D_result

    def abdis_2D(self,abdis2D_mknum1,abdis2D_mknum2):#absolute distance 2D 2点間のx,y方向の絶対値
        
        self.abdis2D_result = math.sqrt(
            ((self.landmarks[abdis2D_mknum1][0] - self.landmarks[abdis2D_mknum2][0]))**2 +
            ((self.landmarks[abdis2D_mknum1][1] - self.landmarks[abdis2D_mknum2][1]))**2
        )
        return self.abdis2D_result

    #指の関節と関節のベクトル 後でhandsignに移動
    def fin_vec_equation(self,joint_num=None,step=1):#equation:方程式 joint_num:第何関節から step:何関節飛びにか
        self.fin_vec_equ_result = []#返り値初期化
        for fin_num in range(joint_num,21,4):#親指から
            self.fingerVec =[
                self.rect_trans()[fin_num][0] - self.rect_trans()[fin_num+step][0],
                self.rect_trans()[fin_num][1] - self.rect_trans()[fin_num+step][1],
                self.rect_trans()[fin_num][2] - self.rect_trans()[fin_num+step][2],
            ]
            #方向ベクトル(a,b,c)において
            #(x-x0)/a = (y-y0)/b = (z-z0)/c より
            #bx-ay = bx0-ay0 と cy-bz = cy0-bz0 が成り立つ
            #[[b,-a,0]    [x,    [bx0-ay0,
            # [0,c,-b]] ・ y,  =  cy0-bz0]
            #              z]
            
            self.fin_vec_equ_result.append([
                [
                    [self.fingerVec[1],-1*self.fingerVec[0],0],
                    [0,self.fingerVec[2],-1*self.fingerVec[1]],
                ],
                [
                    self.fingerVec[1]*self.rect_trans()[fin_num][0] - self.fingerVec[0]*self.rect_trans()[fin_num][1],
                    self.fingerVec[2]*self.rect_trans()[fin_num][2] - self.fingerVec[1]*self.rect_trans()[fin_num][2],
                ]
            ])
        return self.fin_vec_equ_result

    #手のひらの横幅から手の距離を求める
    def palm_dipth(self):
        self.halfof_shwplmwid = self.abdis_3D(5,17) / 2 #5は人差し指の付け根 17は小指の付け根
        self.halfof_shwplmwid_angle = self.MHA * self.halfof_shwplmwid #画角×画像の横幅に対して何倍か で手のひらの幅の角度の半分が求まる
        #z[mm] = 手のひらの横幅の半分[mm] / sin(手のひらの角度の半分)
        self.palm_dipth_info = self.halfof_palm_width / math.sin(self.halfof_shwplmwid_angle)
        return self.palm_dipth_info

    #直交座標変換 rectangular coodinate transform
    def rect_trans(self): 
        #倍率を求める
        self.rectTransMagn = 2*self.halfof_palm_width / self.abdis_3D(5,17)#magnification
        self.rectTrans_result = [] #初期化
        #手首のz座標をpalm_dipthとし、極座標を直交座標として扱っている 後で直す
        for rect_trans_num in range(0,21):
            self.rectTrans_result.append( [
                self.landmarks[rect_trans_num][0]*self.rectTransMagn,
                self.landmarks[rect_trans_num][1]*self.rectTransMagn,
                self.landmarks[rect_trans_num][2]*self.rectTransMagn + self.palm_dipth(),
            ] )
        return self.rectTrans_result

    #結果を返す これをメインで使う
    def handsignText(self):
        #print("手のひらの表裏判別",self.palm_direction())
        #print("中指の付け根の向き",self.midfin_vec())
        #print("指の曲げ伸ばし",self.FingerRaising())

        if self.FingerRaising() == {"5":1, "9":0, '13':-1, '17':-1}:
            self.handSingText_result = "3D_tranceform"

        elif self.palm_direction() == "reverse":
            if self.FingerRaising() == {'5': 1, '9': -1, '13': -1, '17': -1}:
                self.handSingText_result = "choice_mode_move"
            elif self.FingerRaising() == {'5': 1, '9': -1, '13': -1, '17': 1}:
                self.handSingText_result = "choice_mode_cleck"
            
            elif self.FingerRaising() == {'5': 1, '9': 1, '13': 1, '17': 1}:
                if (
                    self.handSingText_result_backup != "keyboard_wait_start" and
                    self.handSingText_result_backup != "keyboard_wait_01" and
                    self.handSingText_result_backup != "keyboard_wait_02"
                    ):
                    self.handSingText_result = "keyboard_wait_start"
                elif self.handSingText_result_backup == "keyboard_wait_01":
                    self.handSingText_result = "keyboard_wait_02"
                #"keyboard_wait_start"か"keyboard_wait_01"ならそのまま


            elif self.FingerRaising() == {'5': -1, '9': -1, '13': -1, '17': -1}:
                if self.handSingText_result_backup == "keyboard_wait_start":
                    self.tm.targetCount("keyboard_wait") #time_mesureモジュールで開始時間設定
                    self.handSingText_result = "keyboard_wait_01"
                elif self.handSingText_result_backup == "keyboard_wait_01": #さっき握ったままならそのまま
                    pass
                elif self.handSingText_result_backup == "keyboard_wait_02":
                    if self.tm.targetCount("keyboard_wait") < 5: #開始時間設定から5秒以内なら
                        self.handSingText_result = "keyboard_open"
                else:
                    self.handSingText_result="握りこぶし コマンドなし"


        elif self.palm_direction() == "overse":
            if self.FingerRaising() == {'5': 1, '9': -1, '13': -1, '17': -1}:
                if self.tm.targetCount("shortcut_1") > 2:#2秒以上経過したなら
                    self.handSingText_result = "shortcut_1"
                else:
                    self.handSingText_result = "shortcut_1_wait"
            if self.FingerRaising() == {'5': 1, '9': 1, '13': -1, '17': -1}:
                if self.tm.targetCount("shortcut_2") > 2:
                    self.handSingText_result = "shortcut_2"
                else:
                    self.handSingText_result = "shortcut_2_wait"
            if self.FingerRaising() == {'5': 1, '9': 1, '13': 1, '17': -1}:
                if self.tm.targetCount("shortcut_3") > 2:
                    self.handSingText_result = "shortcut_3"
                else:
                    self.handSingText_result = "shortcut_3_wait"
            if self.FingerRaising() == {'5': 1, '9': 1, '13': 1, '17': 1}:
                if self.tm.targetCount("shortcut_4") > 2:
                    self.handSingText_result = "shortcut_4"
                else:
                    self.handSingText_result = "shortcut_4_wait"

        elif self.palm_direction() == "sidewayspalm":
            self.handSingText_result = "sidewayspalm"

        self.handSingText_result_backup = self.handSingText_result
        return self.handSingText_result