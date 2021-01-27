import cv2
import numpy as np

class drowing:
    FONT1 = cv2.FONT_HERSHEY_COMPLEX
    FONT2 = cv2.FONT_HERSHEY_COMPLEX_SMALL
    CLEAR_COLOR = (255,255,255)

    #あとで別ファイルにまとめたい
    #キーボードの四角
    KEYBOARD = [ [0,-100,150],[500,-100,150],[500,0,0],[0,0,0] ]
    

    def __init__(self,Img1=None,Img2=None,judge_insname=None,img_pro_insname_L=None,img_pro_insname_R=None):
        self.ImgLeft=Img1#cv2で扱える形にしたもの？
        self.ImgRight=Img2
        self.judge_instance = judge_insname #handsign_judgeのインスタンス
        self.img_pro_insname_L = img_pro_insname_L #左目のimg_processingのインスタンス
        self.img_pro_insname_R = img_pro_insname_R #右目のimg_processingのインスタンス

        self.palm_width = None

        self.object_position_infos={} #オブジェクトの座標 手のひらの横幅を基準に考える

        self.eyeL_procesed_keyboard = [] #移動したキーボードの頂点の座標のリスト
        self.eyeR_procesed_keyboard = []

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
        self.palm_width = self.judge_instance.palm_dipth(self.judge_instance.abdis_2D(5,17)) #画像の横幅分のいくつ で返される
        self.object_position_infos["keyboard"] = self.palm_width
        cv2.putText(self.ImgLeft,str(self.object_position_infos["keyboard"]),(0,40),drowing.FONT1,1,(0,0,0),2)

        #
        eyeL_pointLT=self.img_pro_insname_L.point_processing((-10,50,100))
        eyeL_pointRT=self.img_pro_insname_L.point_processing((10,50,100))
        eyeR_pointLT=self.img_pro_insname_R.point_processing((-10,50,100))
        eyeR_pointRT=self.img_pro_insname_R.point_processing((10,50,100))

        cv2.line(self.ImgLeft,eyeL_pointLT,eyeL_pointRT,(0,0,0)) #引き数で座標指定
        cv2.line(self.ImgRight,eyeR_pointLT,eyeR_pointRT,(0,0,0))
        #

        for i in range(0,5):
            self.eyeL_procesed_keyboard.append = self.img_pro_insname_L.point_processing(drowing.KEYBOARD[i])
            self.eyeR_procesed_keyboard.append = self.img_pro_insname_R.point_processing(drowing.KEYBOARD[i])
        cv2.fillConvexPoly(self.ImgLeft,self.eyeL_procesed_keyboard,(0,0,0))
        cv2.fillConvexPoly(self.ImgRight,self.eyeR_procesed_keyboard,(0,0,0))

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