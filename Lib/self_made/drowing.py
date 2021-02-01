import cv2
import numpy as np
import json

class drowing:
    FONT1 = cv2.FONT_HERSHEY_COMPLEX
    FONT2 = cv2.FONT_HERSHEY_COMPLEX_SMALL
    CLEAR_COLOR = (255,255,255)

    #あとで別ファイルにまとめたい
    #キーボードの四角 原点をスペースキーの下部真ん中とする
    KEYBOARD_BASE = [ [-250,50,250],[300,50,250],[300,0,0],[-250,0,0] ]
    KEYBOARD_BUTTON = [ [-20,5,40],[20,5,40],[20,2,0],[-20,2,0] ] #ボタンの原点はボタンの下部真ん中
    KEYBOARD_SPACE = [ [-50,5,40],[50,5,40],[50,2,0],[-50,2,0] ]
    #enterはキーボード原点から 見ずらいから、隣のキーと1cm空ける
    KEYBOARD_ENTER = [ [260,50,245],[300,50,245],[300,7,55],[260,7,55] ] 
    KEYBOARD_COLOR = (0,0,0)
    KEYBOARD_BUTTON_COLOR = [255,255,0]


    def __init__(self,Img1=None,Img2=None,judge_insname=None,img_pro_insname_L=None,img_pro_insname_R=None):
        self.ImgLeft=Img1#cv2で扱える形にしたもの？
        self.ImgRight=Img2
        self.judge_instance = judge_insname #handsign_judgeのインスタンス
        self.img_pro_insname_L = img_pro_insname_L #左目のimg_processingのインスタンス
        self.img_pro_insname_R = img_pro_insname_R #右目のimg_processingのインスタンス

        self.palm_dipth_info = None

        self.object_position_infos={} #オブジェクトの座標 手のひらの横幅を基準に考える

        self.before_pro_object = [] #加工前のオブジェクトの頂点の座標のリスト
        self.eyeL_ofter_pro_object = [] #加工後のオブジェクトの頂点の座標のリスト
        self.eyeR_ofter_pro_object = []

        self.text_prehansig_backup = None
        self.current_mode = []

    def img_reset(self,reset_range):
        if reset_range == "prehansig":
            #黒で画面全体をクリアする方法わかんなかったら、白の長方形で塗りつぶし
            cv2.rectangle(self.ImgRight,(200,0),(500,50),drowing.CLEAR_COLOR,thickness=-1)
            cv2.rectangle(self.ImgLeft,(200,0),(500,50),drowing.CLEAR_COLOR,thickness=-1)
            
        if reset_range == "current_mode":
            #黒で画面全体をクリアする方法わかんなかったら、白の長方形で塗りつぶし
            cv2.rectangle(self.ImgRight,(200,50),(500,100),drowing.CLEAR_COLOR,thickness=-1)
            cv2.rectangle(self.ImgLeft,(200,50),(500,100),drowing.CLEAR_COLOR,thickness=-1)
        
    def drowing_keyboard(self):
        self.palm_dipth_info = self.judge_instance.palm_dipth() 
        self.object_position_infos["keyboard"] = self.palm_dipth_info
        cv2.putText(self.ImgLeft,str(self.object_position_infos["keyboard"]),(0,40),drowing.FONT1,1,(0,0,0),2)
        cv2.putText(self.ImgRight,str(self.object_position_infos["keyboard"]),(0,40),drowing.FONT1,1,(0,0,0),2)

        self.eyeL_ofter_pro_object=[]#編集後オブジェクト情報を初期化
        self.eyeR_ofter_pro_object=[]
        for i in range(0,4):
            self.before_pro_object=[
                drowing.KEYBOARD_BASE[i][0], 
                drowing.KEYBOARD_BASE[i][1], 
                drowing.KEYBOARD_BASE[i][2]+self.palm_dipth_info
            ]
            self.eyeL_ofter_pro_object.append( self.img_pro_insname_L.point_processing(self.before_pro_object) )
            self.eyeR_ofter_pro_object.append( self.img_pro_insname_R.point_processing(self.before_pro_object) )
        if bool(self.eyeL_ofter_pro_object) == True:#描画距離内なら    
            cv2.fillConvexPoly(self.ImgLeft,np.array(self.eyeL_ofter_pro_object),drowing.KEYBOARD_COLOR)
            cv2.fillConvexPoly(self.ImgRight,np.array(self.eyeR_ofter_pro_object),drowing.KEYBOARD_COLOR)

        #キーボードのボタンを描画
        for k in range(1,5):#縦方向
            for j in range(0,10):#横方向
                self.eyeL_ofter_pro_object=[]#書き込み前に編集後オブジェクト情報を初期化
                self.eyeR_ofter_pro_object=[]
                for i in range(0,4):
                    self.before_pro_object =  [ 
                        drowing.KEYBOARD_BUTTON[i][0]+j*50-225, 
                        drowing.KEYBOARD_BUTTON[i][1]+k*10+4, 
                        #z方向にはさらに手のひらの深さも足す
                        drowing.KEYBOARD_BUTTON[i][2]+k*50+5+self.palm_dipth_info
                    ]
                    self.eyeL_ofter_pro_object.append( self.img_pro_insname_L.point_processing(self.before_pro_object) )
                    self.eyeR_ofter_pro_object.append( self.img_pro_insname_R.point_processing(self.before_pro_object) )
                if self.eyeL_ofter_pro_object:#描画距離外ならcontinue 起こるはずがないけど一応
                    cv2.fillConvexPoly(self.ImgLeft,np.array(self.eyeL_ofter_pro_object),drowing.KEYBOARD_BUTTON_COLOR)
                    cv2.fillConvexPoly(self.ImgRight,np.array(self.eyeR_ofter_pro_object),drowing.KEYBOARD_BUTTON_COLOR)

        self.eyeL_ofter_pro_object=[]
        self.eyeR_ofter_pro_object=[]
        for i in range(0,4):
            self.before_pro_object = [
                drowing.KEYBOARD_ENTER[i][0],
                drowing.KEYBOARD_ENTER[i][1],
                drowing.KEYBOARD_ENTER[i][2]+self.palm_dipth_info,
            ]
            self.eyeL_ofter_pro_object.append( self.img_pro_insname_L.point_processing(self.before_pro_object) )
            self.eyeR_ofter_pro_object.append( self.img_pro_insname_R.point_processing(self.before_pro_object) )
        
        if self.eyeL_ofter_pro_object:#描画距離内なら    
            cv2.fillConvexPoly(self.ImgLeft,np.array(self.eyeL_ofter_pro_object),drowing.KEYBOARD_BUTTON_COLOR)
            cv2.fillConvexPoly(self.ImgRight,np.array(self.eyeR_ofter_pro_object),drowing.KEYBOARD_BUTTON_COLOR)

        self.eyeL_ofter_pro_object=[]
        self.eyeR_ofter_pro_object=[]
        for i in range(0,4):
            self.before_pro_object = [ 
                drowing.KEYBOARD_SPACE[i][0],
                drowing.KEYBOARD_SPACE[i][1],
                drowing.KEYBOARD_SPACE[i][2]+self.palm_dipth_info,
            ]
            self.eyeL_ofter_pro_object.append( self.img_pro_insname_L.point_processing(self.before_pro_object) )
            self.eyeR_ofter_pro_object.append( self.img_pro_insname_R.point_processing(self.before_pro_object) )
        cv2.fillConvexPoly(self.ImgLeft,np.array(self.eyeL_ofter_pro_object),drowing.KEYBOARD_BUTTON_COLOR)
        cv2.fillConvexPoly(self.ImgRight,np.array(self.eyeR_ofter_pro_object),drowing.KEYBOARD_BUTTON_COLOR)
        if self.eyeL_ofter_pro_object:#描画距離内なら    
            cv2.fillConvexPoly(self.ImgLeft,np.array(self.eyeL_ofter_pro_object),drowing.KEYBOARD_BUTTON_COLOR)
            cv2.fillConvexPoly(self.ImgRight,np.array(self.eyeR_ofter_pro_object),drowing.KEYBOARD_BUTTON_COLOR)

        #with open("Obect_info/keyboard.json") as KEYBOARD_JSON:
        #    key_position= np.array(KEYBOARD_JSON["key"])
            

    def drowing_3Dview(self,text_prehansig): #present handsign 現在のハンドサイン
            
        ##PIL型をopenCV型に変換 PIL型とは？
        #new_image = np.array(ImgLeft, dtype=np.uint8)
        #new_image = cv2.cvtColor(new_image, cv2.COLOR_RGB2BGR)

        if self.text_prehansig_backup != text_prehansig: #1つ前のtext_prehansigと違うなら
            self.img_reset("prehansig")
            self.text_prehansig_backup = text_prehansig

            cv2.putText(self.ImgLeft,text_prehansig,(200,40),drowing.FONT1,1,(0,0,0),2)
            cv2.putText(self.ImgRight,text_prehansig,(200,40),drowing.FONT1,1,(0,0,0),2)

        if text_prehansig == "keyboard_open":
            if not "keyboard" in self.current_mode:
                self.current_mode.append("keyboard")
                self.drowing_keyboard()
            cv2.putText(self.ImgLeft,str(self.current_mode),(200,80),drowing.FONT2,1,(0,155,0),2)
            cv2.putText(self.ImgRight,str(self.current_mode),(200,80),drowing.FONT2,1,(0,155,0),2)
            

        print("現在のハンドサインは",text_prehansig,"画像への書き込み完了\n")