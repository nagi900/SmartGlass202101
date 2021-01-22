import numpy as np
import math

class handsign_judge_1:

    def __init__(self):
        self.landmarks = {}
        self.landmark_x=0.0
        self.landmark_y=0.0
        self.landmark_z=0.0

        self.FrontorBack_info="a"##手のひらの裏表を判別　FrontorBackで使用

        self.middlefingure_vector_x=0.0
        self.middlefingure_vector_y=0.0
        self.middlefingure_vector_z=0.0
        self.middlefingure_vector_1ofzettaichi=0.0
        self.middlefingure_vector=[]

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

        self.result_info="a"

    #まずこれを呼び出して設定
    def setting(self,idx,landmark_x,landmark_y,landmark_z):#landmark):#
        self.idx=idx
        #self.landmark=landmark
        self.landmark_x=landmark_x
        self.landmark_y=landmark_y
        self.landmark_z=landmark_z
        this_idx_position=[self.landmark_x,self.landmark_y,self.landmark_z]
        
        self.landmarks[self.idx] = this_idx_position #self.landmark

    #手のひらの裏表を判別
    def FrontorBack(self):
        if self.landmarks[5][0]<self.landmarks[17][0]:#右手で人差し指の付け根が小指の付け根より左にあるなら
            self.FrontorBack_info = "overse"
        else :
            self.FrontorBack_info = "reverse"
        return self.FrontorBack_info

    #中指の付け根のの向きを判別
    def MiddlefingerVector(self):
        self.middlefingure_vector_x=self.landmarks[9][0] - self.landmarks[0][0]
        self.middlefingure_vector_y=self.landmarks[9][1] - self.landmarks[0][1]
        self.middlefingure_vector_z=self.landmarks[9][2] - self.landmarks[0][2]
        #(1/ベクトルの絶対値)を求める
        self.middlefingure_vector_1ofzettaichi = 1 / math.sqrt(
            self.middlefingure_vector_x**2+
            self.middlefingure_vector_y**2+
            self.middlefingure_vector_z**2
        )
        #各ベクトルに(1/ベクトルの絶対値)を掛ける
        self.middlefingure_vector_info =  [
                self.middlefingure_vector_1ofzettaichi*self.middlefingure_vector_x,
                self.middlefingure_vector_1ofzettaichi*self.middlefingure_vector_y,
                self.middlefingure_vector_1ofzettaichi*self.middlefingure_vector_z
        ]
        return self.middlefingure_vector_info

    def FingerRaising(self):
        #法線ベクトルn(x_n,y_n,z_n) の 点A(x_a,y_a,z_a) を含む面S
        #任意の面上の点P(x_p,y_p,z_p) を考える
        #APとnは垂直 ∴AP・n=0 
        #空間内の任意の点Q(x_q,y_q,z_q) を考えると　AQ・n>0なら面Sよりnベクトル方向に正
        for i in range(5,18,4):
            self.x_n,self.y_n,self.z_n=self.MiddlefingerVector()
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
            if self.FingerRaising_value > 0:
                self.FingerRaising_info[str(i)] = 1
            else :
                self.FingerRaising_info[str(i)] = -1
        return self.FingerRaising_info

    #結果を返す これをメインで使う
    def result(self):
        print("手のひらの表裏判別",self.FrontorBack())
        print("中指の付け根の向き",self.MiddlefingerVector())
        print("指の曲げ伸ばし",self.FingerRaising())

        if self.FrontorBack_info == "reverse":
            if self.FingerRaising() == {'5': 1, '9': 1, '13': -1, '17': -1}:
                self.result_info = "choice_mode_move"
            elif self.FingerRaising() == {'5': 1, '9': -1, '13': -1, '17': 1}:
                self.result_info = "choice_mode_cleck"

        elif self.FrontorBack_info == "overse":
            if self.FingerRaising() == {'5': 1, '9': -1, '13': -1, '17': -1}:
                self.result_info = "shortcut_1"
            if self.FingerRaising() == {'5': 1, '9': 1, '13': -1, '17': -1}:
                self.result_info = "shortcut_2"
            if self.FingerRaising() == {'5': 1, '9': 1, '13': 1, '17': -1}:
                self.result_info = "shortcut_3"
            if self.FingerRaising() == {'5': 1, '9': 1, '13': 1, '17': 1}:
                self.result_info = "shortcut_4"

        return self.result_info

    def test(self):
        return self.landmarks

#後で聞くこと　self.って毎回つけなきゃいけないの？　クラス変数じゃなくても？
#使う関数は全部__init__に定義しなきゃいけないの？　初期化の役割もあるからそうかも
#上の続き　一つの関数内でしか使わなければok？

if __name__ == "__main__":#直接起動した場合テストする
    print("テストします")
    hoge1=handsign_judge_1()
    hoge2=handsign_judge_1()
    hoge1.setting(0,1.9,12.0,1234)
    hoge1.setting(1,1.9,12.0,1234)
    hoge2.setting(2,1.9,12.0,1234)
    hoge2.setting(3,1.9,12.0,1234)
    print(hoge1.test(),"\n",hoge2.test())