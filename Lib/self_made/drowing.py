import cv2
import numpy as np
import json

class drowing:#モードの記述や画面クリアなどで、相対座標ではなく、絶対座標から指定してしまっている imgproccesingとか使って相対座標で描けるように
    FONT1 = cv2.FONT_HERSHEY_COMPLEX
    FONT2 = cv2.FONT_HERSHEY_COMPLEX_SMALL
    CLEAR_COLOR = [255,255,255]
    KEYBOARD_BASE = [ [-250,50,250],[300,50,250],[300,0,0],[-250,0,0] ]

    KEYBOARD_BASE_COLOR = [0,0,0]
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

        
        #OBJ2List 参考元 http://www.cloud.teu.ac.jp/public/MDF/toudouhk/blog/2015/01/15/OBJTips/
        self.numVertices = 0
        self.numUVs = 0
        self.numNormals = 0
        self.numFaces = 0
        self.vertices = []
        self.uvs = []
        self.normals = []
        self.vertexColors = []
        self.faceVertIDs = []
        self.uvIDs = []
        self.normalIDs = []

        self.LOADED_KEYBOARD_JSON = None
        self.key_position = None

    def img_reset(self,reset_range):#画面クリア
        if reset_range == "prehansig":
            #黒で画面全体をクリアする方法わかんなかったら、白の長方形で塗りつぶし
            cv2.rectangle(self.ImgRight,(200,0),(500,50),drowing.CLEAR_COLOR,thickness=-1)
            cv2.rectangle(self.ImgLeft,(200,0),(500,50),drowing.CLEAR_COLOR,thickness=-1)
            
        if reset_range == "current_mode":
            #黒で画面全体をクリアする方法わかんなかったら、白の長方形で塗りつぶし
            cv2.rectangle(self.ImgRight,(200,50),(500,100),drowing.CLEAR_COLOR,thickness=-1)
            cv2.rectangle(self.ImgLeft,(200,50),(500,100),drowing.CLEAR_COLOR,thickness=-1)
        
        if reset_range == "object":
            cv2.fillConvexPoly(self.ImgRight,np.array([
                (0,0),(0,50),(200,50),(200,100),(500,100),(500,500),(0,500)
            ]),drowing.CLEAR_COLOR)
            cv2.fillConvexPoly(self.ImgLeft,np.array([
                (0,0),(0,50),(200,50),(200,100),(500,100),(500,500),(0,500)
            ]),drowing.CLEAR_COLOR)

        if reset_range == "all":
            cv2.rectangle(self.ImgRight,(0,0),(500,500),drowing.CLEAR_COLOR,thickness=-1)
            cv2.rectangle(self.ImgLeft,(0,0),(500,500),drowing.CLEAR_COLOR,thickness=-1)
        

        #objファイルをリストにする
    def OBJ2List(self,path):
        for line in open(path, "r"):
            vals = line.split()
            if len(vals) == 0:
                continue
            if vals[0] == "v":
                v = vals[1:4]
                self.vertices.append(v)
                if len(vals) == 7:
                    vc = vals[4:7]
                    self.vertexColors.append(vc)
                self.numVertices += 1
            if vals[0] == "vt":
                vt = vals[1:3]
                self.uvs.append(vt)
                self.numUVs += 1
            if vals[0] == "vn":
                vn = vals[1:4]
                self.normals.append(vn)
                self.numNormals += 1
            if vals[0] == "f":
                fvID = []
                uvID = []
                nvID = []
                for f in vals[1:]:
                    w = f.split("/")
                    if self.numVertices > 0:
                        fvID.append(int(w[0])-1)
                    if self.numUVs > 0:
                        uvID.append(int(w[1])-1)
                    if self.numNormals > 0:
                        nvID.append(int(w[2])-1)
                self.faceVertIDs.append(fvID)
                self.uvIDs.append(uvID)
                self.normalIDs.append(nvID)
                self.numFaces += 1
        return self.vertices, self.uvs, self.normals, self.faceVertIDs, self.uvIDs, self.normalIDs, self.vertexColors

    def drowing_keyboard(self):
        self.palm_dipth_info = self.judge_instance.palm_dipth()#rect_trans_info[0][2]と一緒だからこれ要らないかも
        self.rect_trans_info = self.judge_instance.rect_trans()
        self.object_position_infos["keyboard"] = self.palm_dipth_info
        cv2.putText(self.ImgLeft,str(self.object_position_infos["keyboard"]),(0,40),drowing.FONT1,1,(0,0,0),2)
        cv2.putText(self.ImgRight,str(self.object_position_infos["keyboard"]),(0,40),drowing.FONT1,1,(0,0,0),2)

        self.eyeL_ofter_pro_object=[]#編集後オブジェクト情報を初期化
        self.eyeR_ofter_pro_object=[]
        for i in range(0,4):
            self.before_pro_object=[
                drowing.KEYBOARD_BASE[i][0], 
                drowing.KEYBOARD_BASE[i][1]+self.rect_trans_info[0][1], 
                drowing.KEYBOARD_BASE[i][2]+self.palm_dipth_info
            ]
            self.eyeL_ofter_pro_object.append( self.img_pro_insname_L.point_processing(self.before_pro_object) )
            self.eyeR_ofter_pro_object.append( self.img_pro_insname_R.point_processing(self.before_pro_object) )
        if (not None in self.eyeL_ofter_pro_object) and (not None in self.eyeR_ofter_pro_object):#描画距離内なら    
            cv2.fillConvexPoly(self.ImgLeft,np.array(self.eyeL_ofter_pro_object),drowing.KEYBOARD_BASE_COLOR)
            cv2.fillConvexPoly(self.ImgRight,np.array(self.eyeR_ofter_pro_object),drowing.KEYBOARD_BASE_COLOR)

        with open("Object_info/keyboard.json") as KEYBOARD_JSON:
            self.LOADED_KEYBOARD_JSON = json.load(KEYBOARD_JSON) #jsonとしてロード(読み込み)する必要あり
            self.key_position = self.LOADED_KEYBOARD_JSON["key"]
            for horolist in self.key_position:
                for keybox_and_name in horolist:
                    self.eyeL_ofter_pro_object=[]
                    self.eyeR_ofter_pro_object=[]
                    for keybox in keybox_and_name[0]:
                        self.before_pro_object = [
                            keybox[0],
                            keybox[1]+self.rect_trans_info[0][1],
                            keybox[2]+self.palm_dipth_info,
                        ]
                        self.eyeL_ofter_pro_object.append( self.img_pro_insname_L.point_processing(self.before_pro_object) )
                        self.eyeR_ofter_pro_object.append( self.img_pro_insname_R.point_processing(self.before_pro_object) )
                    if (not None in self.eyeL_ofter_pro_object) and (not None in self.eyeR_ofter_pro_object):#描画距離内なら
                        cv2.fillConvexPoly(self.ImgLeft,np.array(self.eyeL_ofter_pro_object),drowing.KEYBOARD_BUTTON_COLOR)#drowing.KEYBOARD_BUTTON_COLOR)
                        cv2.fillConvexPoly(self.ImgRight,np.array(self.eyeR_ofter_pro_object),drowing.KEYBOARD_BUTTON_COLOR)
            
    def drowing_OBJ(self,path,magnification=[1,1,1],rotation=[1,1,1],translation=[0,0,0]):#mgnification:拡大 rotation:回転 taranslation:平行移動
        obj_list=self.OBJ2List(path)
        obj_pointS = obj_list[0]
        for obj_point in obj_pointS:
            obj_point = [ 
                float(obj_point[0])*magnification[0] *rotation[0] +translation[0],
                float(obj_point[1])*magnification[1] *rotation[1] +translation[1],
                float(obj_point[2])*magnification[2] *rotation[2] +translation[2],
            ]
            if ( self.img_pro_insname_L.point_processing(obj_point) ) and ( self.img_pro_insname_R.point_processing(obj_point) ): 
                cv2.circle(self.ImgLeft, self.img_pro_insname_L.point_processing(obj_point) ,1,(int(obj_point[2]*0.5),int(obj_point[2]*0.5), int(obj_point[2]*0.5) ))
                cv2.circle(self.ImgRight, self.img_pro_insname_R.point_processing(obj_point) ,1,(int(obj_point[2]*0.5),int(obj_point[2]*0.5), int(obj_point[2]*0.5) ))

    def drowing_landmarks(self):
        self.eyeL_ofter_pro_object=[]
        self.eyeR_ofter_pro_object=[]
        for transd_lndmrk in self.judge_instance.rect_trans():
            if self.img_pro_insname_L.point_processing(transd_lndmrk) and self.img_pro_insname_R.point_processing(transd_lndmrk):#描画距離内なら
                cv2.circle(self.ImgLeft, self.img_pro_insname_L.point_processing(transd_lndmrk) ,3,(255,0,0),2)
                cv2.circle(self.ImgRight, self.img_pro_insname_R.point_processing(transd_lndmrk) ,3,(255,0,0),2)

    def drowing_3Dview(self,text_prehansig,mode=None): #present handsign 現在のハンドサイン
        if mode == "drowing hand":
            self.img_reset("object")
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
                self.img_reset("current_mode")
                self.current_mode.append("keyboard")
                self.drowing_keyboard()
                cv2.putText(self.ImgLeft,str(self.current_mode),(200,80),drowing.FONT2,1,(0,155,0),2)
                cv2.putText(self.ImgRight,str(self.current_mode),(200,80),drowing.FONT2,1,(0,155,0),2)
            
        if text_prehansig == "shortcut_4":
            if not "3Dobject" in self.current_mode:
                self.img_reset("current_mode")
                self.current_mode.append("3Dobject")
                self.drowing_OBJ("../nogit_object/12140_Skull_v3_L2.obj",[10,10,10])
                cv2.putText(self.ImgLeft,str(self.current_mode),(200,80),drowing.FONT2,1,(0,155,0),2)
                cv2.putText(self.ImgRight,str(self.current_mode),(200,80),drowing.FONT2,1,(0,155,0),2)

        if mode == "drowing hand":
            self.drowing_landmarks()