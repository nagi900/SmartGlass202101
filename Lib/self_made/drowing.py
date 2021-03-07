import cv2
import numpy as np
import json
import math
import traceback
from PIL import Image

class drowing:#モードの記述や画面クリアなどで、相対座標ではなく、絶対座標から指定してしまっている imgproccesingとか使って相対座標で描けるように
    FONT1 = cv2.FONT_HERSHEY_COMPLEX
    FONT2 = cv2.FONT_HERSHEY_COMPLEX_SMALL
    FONT_COLOR = [0,0,0,255]
    CLEAR_COLOR = [255,255,255,255]
    ALPHA_COLOR = [0,0,0,0]
    KEYBOARD_BASE = [ [-250,50,250],[300,50,250],[300,0,0],[-250,0,0] ]
    KEYBOARD_BASE_COLOR = [0,0,0,255]
    KEYBOARD_BUTTON_COLOR = [255,255,0,255]


    def __init__(self,Leftlayers=None,Rightlayers=None,judge_insname=None,img_pro_insname_L=None,img_pro_insname_R=None,window_pxl_shape=None):
        self.ImgLeft_Object = Leftlayers[0]#レイヤーのインデックスが大きいほど手前に idxとレイヤーの前後関係はhandtracking.pyの合成順で定義
        self.ImgRight_Object = Rightlayers[0]
        self.ImgLeft_Keyboard = Leftlayers[1]
        self.ImgRight_Keyboard = Rightlayers[1]
        self.ImgLeft_Hand = Leftlayers[2]
        self.ImgRight_Hand = Rightlayers[2]
        self.ImgLeft_Mode = Leftlayers[3]
        self.ImgRight_Mode = Rightlayers[3]

        self.judge_instance = judge_insname #handsign_judgeのインスタンス
        self.img_pro_insname_L = img_pro_insname_L #左目のimg_processingのインスタンス
        self.img_pro_insname_R = img_pro_insname_R #右目のimg_processingのインスタンス

        self.window_pxl_width = window_pxl_shape[0]#表示する画像の幅
        self.window_pxl_hight = window_pxl_shape[1]

        self.wheather_merging = {1:1,2:1,3:0}#それぞれのlayerをマージするかどうか

        self.palm_dipth_info = None

        self.object_position_infos={} #オブジェクトの座標 手のひらの横幅を基準に考える

        self.before_pro_object = [] #加工前のオブジェクトの頂点の座標のリスト
        self.eyeL_ofter_pro_object = [] #加工後のオブジェクトの頂点の座標のリスト
        self.eyeR_ofter_pro_object = []

        self.text_prehansig_backup = None
        self.current_mode = []

        #OBJ2List
        self.OBJ2List_path_backup=None
        self.OBJ2List_result_backup={}#keyがpathの辞書
        # 参考元 http://www.cloud.teu.ac.jp/public/MDF/toudouhk/blog/2015/01/15/OBJTips/
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

        #drowing_keyboard
        self.LOADED_KEYBOARD_JSON = None
        self.key_position = None
        self.slided_key_positions_ver = []#縦方向に区切るリスト slided_key_positionに代入するときしか使わない
        self.slided_key_positions = []

        

        #drowing_hand
        self.hand_landmarks_color=[255,0,0,255]
        

    def img_reset(self,layer_name,reset_range):#画面クリア
        if layer_name == "object":
            self.img_reset_layer = [self.ImgLeft_Object,self.ImgRight_Object]
            if reset_range == "object":
                cv2.fillConvexPoly(self.img_reset_layer[0],np.array([
                    (0,0),(200,0),(200,50),(200,100),(500,100),(500,500),(0,500)
                ]),drowing.CLEAR_COLOR)
                cv2.fillConvexPoly(self.img_reset_layer[1],np.array([
                    (0,0),(0,50),(200,50),(200,100),(500,100),(500,500),(0,500)
                ]),drowing.CLEAR_COLOR)
            if reset_range == "all":
                cv2.rectangle(self.img_reset_layer[0],(0,0),(500,500),drowing.CLEAR_COLOR,thickness=-1)
                cv2.rectangle(self.img_reset_layer[1],(0,0),(500,500),drowing.CLEAR_COLOR,thickness=-1)
                
        else:#objectでなければ透明で塗りつぶし
            if layer_name == "mode":
                self.img_reset_layer = [self.ImgLeft_Mode,self.ImgRight_Mode]
            elif layer_name == "hand":
                self.img_reset_layer = [self.ImgLeft_Hand,self.ImgRight_Hand]
            elif layer_name == "keyboard":
                self.img_reset_layer = [self.ImgLeft_Keyboard,self.ImgRight_Keyboard]
            else:
                try:
                    raise Exception
                except:
                    traceback.print_exc()
                    print("リセットする画像が正しく指定されていません")

            if reset_range == "prehansig":
                #透明の長方形で塗りつぶし
                cv2.rectangle(self.img_reset_layer[0],(200,0),(500,50),drowing.ALPHA_COLOR,thickness=-1)
                cv2.rectangle(self.img_reset_layer[1],(200,0),(500,50),drowing.ALPHA_COLOR,thickness=-1)
                
            if reset_range == "current_mode":
                cv2.rectangle(self.img_reset_layer[0],(200,50),(500,100),drowing.ALPHA_COLOR,thickness=-1)
                cv2.rectangle(self.img_reset_layer[1],(200,50),(500,100),drowing.ALPHA_COLOR,thickness=-1)
            
            if reset_range == "object":
                cv2.fillConvexPoly(self.img_reset_layer[0],np.array([
                    (0,0),(200,0),(200,50),(200,100),(500,100),(500,500),(0,500)
                ]),drowing.ALPHA_COLOR)
                cv2.fillConvexPoly(self.img_reset_layer[1],np.array([
                    (0,0),(0,50),(200,50),(200,100),(500,100),(500,500),(0,500)
                ]),drowing.ALPHA_COLOR)

            if reset_range == "all":
                cv2.rectangle(self.img_reset_layer[0],(0,0),(500,500),drowing.ALPHA_COLOR,thickness=-1)
                cv2.rectangle(self.img_reset_layer[1],(0,0),(500,500),drowing.ALPHA_COLOR,thickness=-1)
        

        #objファイルをリストにする
    def OBJ2List(self,path):
        #すでに読み込まれていたものであれば 
        if path in self.OBJ2List_result_backup:#self.OBJ2List_result_backup.key()と同じ
            return self.OBJ2List_result_backup[path]
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
        self.OBJ2List_result_backup[path] =[ self.vertices, self.uvs, self.normals, self.faceVertIDs, self.uvIDs, self.normalIDs, self.vertexColors ]
        return self.OBJ2List_result_backup[path]

    def drowing_keyboard(self):
        self.palm_dipth_info = self.judge_instance.palm_dipth()#rect_trans_info[0][2]と一緒だからこれ要らないかも
        self.rect_trans_info = self.judge_instance.rect_trans()
        self.object_position_infos["keyboard"] = self.palm_dipth_info
        cv2.putText(self.ImgLeft_Mode,str(self.object_position_infos["keyboard"]),(0,40),drowing.FONT1,1,(0,0,0),2)
        cv2.putText(self.ImgRight_Mode,str(self.object_position_infos["keyboard"]),(0,40),drowing.FONT1,1,(0,0,0),2)

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
            cv2.fillConvexPoly(self.ImgLeft_Keyboard,np.array(self.eyeL_ofter_pro_object),drowing.KEYBOARD_BASE_COLOR)
            cv2.fillConvexPoly(self.ImgRight_Keyboard,np.array(self.eyeR_ofter_pro_object),drowing.KEYBOARD_BASE_COLOR)

        with open("Object_info/keyboard.json") as KEYBOARD_JSON:
            self.LOADED_KEYBOARD_JSON = json.load(KEYBOARD_JSON) #jsonとしてロード(読み込み)する必要あり
            self.key_position = self.LOADED_KEYBOARD_JSON["key"]
            for horolist in self.key_position:
                for keybox_and_name in horolist:
                    self.eyeL_ofter_pro_object=[]
                    self.eyeR_ofter_pro_object=[]
                    self.slided_key_position_keyrect=[]#keyの四隅の座標
                    for keybox in keybox_and_name[0]:
                        self.before_pro_object = [
                            keybox[0],
                            keybox[1]+math.floor(self.rect_trans_info[0][1]),
                            keybox[2]+math.floor(self.palm_dipth_info),
                        ]
                        self.slided_key_position_keyrect.append(self.before_pro_object)
                        self.eyeL_ofter_pro_object.append( self.img_pro_insname_L.point_processing(self.before_pro_object) )
                        self.eyeR_ofter_pro_object.append( self.img_pro_insname_R.point_processing(self.before_pro_object) )
                    if (not None in self.eyeL_ofter_pro_object) and (not None in self.eyeR_ofter_pro_object):#描画距離内なら
                        cv2.fillConvexPoly(self.ImgLeft_Keyboard,np.array(self.eyeL_ofter_pro_object),drowing.KEYBOARD_BUTTON_COLOR)#drowing.KEYBOARD_BUTTON_COLOR)
                        cv2.fillConvexPoly(self.ImgRight_Keyboard,np.array(self.eyeR_ofter_pro_object),drowing.KEYBOARD_BUTTON_COLOR)

                    self.slided_key_positions_ver.append([self.slided_key_position_keyrect,keybox_and_name[1]])#ずらしたキーボードの座標と名前を記録
                self.slided_key_positions.append(self.slided_key_positions_ver)


    def keybaord_typing(self):
        self.typing_mat_2 = self.judge_instance.fin_vec_equation(3)#押したかどうか判別する行列の2行目まで(指の行列)と答えを取得
        #テスト用　人差し指とキーボードのベースの交点
        if (
            #self.judge_instance.rect_trans()[(1+1)*4-2][1] < self.slided_key_positions[4][0][0][0][1] and self.judge_instance.rect_trans()[(1+1)*4][1] > self.slided_key_positions[0][0][0][2][1] and 
            self.judge_instance.rect_trans()[(1+1)*4-2][2] < self.slided_key_positions[4][0][0][0][2] and self.judge_instance.rect_trans()[(1+1)*4][2] > self.slided_key_positions[0][0][0][2][2]  and 
            self.judge_instance.rect_trans()[(1+1)*4-2][0] < self.slided_key_positions[1][9][0][0][0] and self.judge_instance.rect_trans()[(1+1)*4][0] > self.slided_key_positions[1][0][0][0][0]
        ):
            print("人差し指キーボードの範囲内には入ってる")
        else:
            print("入ってない")
        self.test_space_cross = (
            np.round(np.matrix([
                self.typing_mat_2[1][0][0],
                self.typing_mat_2[1][0][1],
                [0,1,0],
            ])**-1)*
            np.matrix([
                np.round([self.typing_mat_2[1][1][0],0,0]),
                np.round([self.typing_mat_2[1][1][1],0,0]),
                np.round([self.slided_key_positions[0][0][0][0][1],0,0]),
            ])
        )
        print(
            "人差し指の向きは",self.typing_mat_2[1][0],"\n",
            "x",self.judge_instance.rect_trans()[(1+1)*4-2][0] ,self.slided_key_positions[1][9][0][0][0], self.slided_key_positions[1][0][0][0][0],"\n",
            "y",self.judge_instance.rect_trans()[(1+1)*4-2][1] , self.slided_key_positions[4][0][0][0][1],self.slided_key_positions[0][0][0][2][1],"\n",
            "z",self.judge_instance.rect_trans()[(1+1)*4-2][2] ,self.slided_key_positions[4][0][0][0][2], self.slided_key_positions[0][0][0][2][2],"\n",
            "スペースキーの高さは",self.slided_key_positions[0][0][0][0][1],"\n"
            "スペースキーの平面との交点は\n",
            self.test_space_cross,"\n"
        )
        #交点を黒で表示
        cv2.circle(self.ImgLeft_Hand, self.img_pro_insname_L.point_processing([
            self.test_space_cross[0,0],self.test_space_cross[1,0],self.test_space_cross[2,0]
        ]),30,(0,0,0,255),5)
        cv2.circle(self.ImgRight_Hand, self.img_pro_insname_R.point_processing([
            self.test_space_cross[0,0],self.test_space_cross[1,0],self.test_space_cross[2,0]
        ]),30,(0,0,0,255),5)
        #人差し指の直線を緑で表示
        cv2.line(
            self.ImgLeft_Hand, 
            self.img_pro_insname_L.point_processing(
                self.judge_instance.rect_trans()[6]
            ),
            self.img_pro_insname_L.point_processing(
                self.judge_instance.rect_trans()[8]
            ),
            (0,255,0,255),
            3
        )
        cv2.line(
            self.ImgRight_Hand, 
            self.img_pro_insname_R.point_processing(
                self.judge_instance.rect_trans()[6]
            ),
            self.img_pro_insname_L.point_processing(
                self.judge_instance.rect_trans()[8]
            ),
            (0,255,0,255),
            3
        )
        if (
            self.img_pro_insname_L.point_processing([self.test_space_cross[0,0],self.test_space_cross[1,0],self.test_space_cross[2,0]])
        ):
            if (
                self.img_pro_insname_L.point_processing([self.test_space_cross[0,0],self.test_space_cross[1,0],self.test_space_cross[2,0]])[0] > 100 and 
                self.img_pro_insname_L.point_processing([self.test_space_cross[0,0],self.test_space_cross[1,0],self.test_space_cross[2,0]])[0] < 400 and
                self.img_pro_insname_L.point_processing([self.test_space_cross[0,0],self.test_space_cross[1,0],self.test_space_cross[2,0]])[1] > 100 and
                self.img_pro_insname_L.point_processing([self.test_space_cross[0,0],self.test_space_cross[1,0],self.test_space_cross[2,0]])[1] < 400
            ):
                print("交点が画面の中央！")
                cv2.imwrite("test/cross_result.png",self.ImgLeft_Hand)

        for i in range(0,6):#keyの行
            for j in range(0,11):#keyの列
                for k in range(0,5):#指
                    self.mat = np.matrix([
                        self.typing_mat_2[k][0][0],
                        self.typing_mat_2[k][0][1],
                        [0,1,0],
                    ])
                    self.cross_point = np.dot(#dotも*も列数行数が一致していないと計算できないっぽい
                        (np.round(self.mat**-1)),
                        np.matrix([
                            np.round([self.typing_mat_2[k][1][0],0,0]),
                            np.round([self.typing_mat_2[k][1][1],0,0]),
                            np.round([self.slided_key_positions[i][j][0][0][1],0,0]),
                        ])
                    )
                    #print("keyの値",self.slided_key_positions[i][j][0][0][2])
                    #print(
                    #    "\n真偽値の判断に使う値",
                    #    self.judge_instance.rect_trans()[(k+1)*4-2][2],
                    #    self.slided_key_positions[i][j][0][0][2] ,
                    #    self.cross_point[1,0],
                    #    self.judge_instance.rect_trans()[(k+1)*4-2][1] <= self.cross_point[1,0],
                    #    self.slided_key_positions[i][j][0][0][0] <= self.cross_point[0][0]
                    #)
                    #cross_point = [ [x 0 0],[y 0 0],[z 0 0] ]

                        #slided_key_position[i][j][0]は
                        #左奥頂点0    右奥頂点1
                        #左手前頂点3　右手前頂点2
                        #x,zはキーボードの中yは手の高さ内
                    if (
                        (self.slided_key_positions[i][j][0][0][0] <= self.cross_point[0,0] ) and (self.cross_point[0,0] <= self.slided_key_positions[i][j][0][1][0] ) and
                        (self.slided_key_positions[i][j][0][0][2] <= self.cross_point[2,0] ) and (self.cross_point[2,0] <= self.slided_key_positions[i][j][0][3][2] ) and
                        (self.judge_instance.rect_trans()[(k+1)*4-2][1] <= self.cross_point[1,0] ) and ( self.cross_point[1,0] <= self.judge_instance.rect_trans()[(k+1)*4][1] )
                    ):
                        print("指",k,self.slided_key_positions[i][j][1])
                    else:
                        #print(
                        #    #"指",k,"の位置は",self.judge_instance.rect_trans()[(k+1)*4-2],self.judge_instance.rect_trans()[(k+1)*4],
                        #    "指",k,"key",self.slided_key_positions[i][j][1],"打ってない 交点は",self.cross_point[0,0],self.cross_point[1,0],self.cross_point[2,0]
                        #)
                        pass

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
                cv2.circle(self.ImgLeft_Object, self.img_pro_insname_L.point_processing(obj_point) ,1,(int(obj_point[2]*0.5),int(255-obj_point[2]*0.5), int(obj_point[2]*0.5) ))
                cv2.circle(self.ImgRight_Object, self.img_pro_insname_R.point_processing(obj_point) ,1,(int(obj_point[2]*0.5),int(255-obj_point[2]*0.5), int(obj_point[2]*0.5) ))

    #手を書く 現時点では点のみ
    def drowing_hand_landmarks(self):
        self.eyeL_ofter_pro_object=[]
        self.eyeR_ofter_pro_object=[]
        for transd_lndmrk in self.judge_instance.rect_trans():
            if self.img_pro_insname_L.point_processing(transd_lndmrk) and self.img_pro_insname_R.point_processing(transd_lndmrk):#描画距離内なら
                cv2.circle(self.ImgLeft_Hand, self.img_pro_insname_L.point_processing(transd_lndmrk) ,3,self.hand_landmarks_color,2)
                cv2.circle(self.ImgRight_Hand, self.img_pro_insname_R.point_processing(transd_lndmrk) ,3,self.hand_landmarks_color,2)

    def drowing_3Dview(self,text_prehansig,mode=None): #present handsign 現在のハンドサイン
        self.img_reset("object","all")#オブジェクトレイヤーをリセットするんじゃなく、ベースレイヤーを作った方がいい気がする

        if mode == "drowing_hand":
            self.img_reset("hand","all")
            self.drowing_hand_landmarks()

        if self.text_prehansig_backup != text_prehansig: #1つ前のtext_prehansigと違うなら
            self.img_reset("mode","prehansig")
            self.text_prehansig_backup = text_prehansig
            cv2.putText(self.ImgLeft_Mode,text_prehansig,(200,40),drowing.FONT1,1,drowing.FONT_COLOR,2)
            cv2.putText(self.ImgRight_Mode,text_prehansig,(200,40),drowing.FONT1,1,drowing.FONT_COLOR,2)

        if text_prehansig == "keyboard_open":
            if not "keyboard" in self.current_mode:
                self.img_reset("mode","current_mode")
                self.current_mode.append("keyboard")
                self.drowing_keyboard()
                cv2.putText(self.ImgLeft_Mode,str(self.current_mode),(200,80),drowing.FONT2,1,drowing.FONT_COLOR,2)
                cv2.putText(self.ImgRight_Mode,str(self.current_mode),(200,80),drowing.FONT2,1,drowing.FONT_COLOR,2)
        
        if (
            "keyboard" in self.current_mode and#keyboardが存在して keyboardのspacekeyの座標より上下10cm,手前10cmから一番奥のキーまで、zkeyの左から/keyの右まで　なら
            self.judge_instance.rect_trans()[0][1] < self.slided_key_positions[0][0][0][0][1]+100 and self.judge_instance.rect_trans()[0][1] > self.slided_key_positions[0][0][0][0][1]-100 and 
            self.judge_instance.rect_trans()[0][2] < self.slided_key_positions[4][0][0][0][2] and self.judge_instance.rect_trans()[0][2] > self.slided_key_positions[0][0][0][0][2]-100  and 
            self.judge_instance.rect_trans()[0][0] < self.slided_key_positions[1][9][0][0][0] and self.judge_instance.rect_trans()[0][0] > self.slided_key_positions[1][0][0][0][0]
        ):
            self.hand_landmarks_color=[0,0,255,255]#手の色を変える
            self.keybaord_typing()
        else:
            self.hand_landmarks_color=[255,0,0,255]
            
        #if text_prehansig == "shortcut_4":
        #    if not "3Dobject" in self.current_mode:
        #        self.img_reset("current_mode")
        #        self.current_mode.append("3Dobject")#キーボード消えちゃうからとりあえず画面消去はしない
        #        self.drowing_OBJ("../nogit_object/12140_Skull_v3_L2.obj",[10,10,10],translation=[0,0,self.judge_instance.palm_dipth()])#40cm先に表示
        #        cv2.putText(self.ImgLeft_Mode,str(self.current_mode),(200,80),drowing.FONT2,1,drowing.FONT_COLOR,2)
        #        cv2.putText(self.ImgRight_Mode,str(self.current_mode),(200,80),drowing.FONT2,1,drowing.FONT_COLOR,2)

        if text_prehansig == "3D_tranceform" and "3Dobject" in self.current_mode:
            self.img_reset("mode","all")
            self.current_mode.append("3Dobject")
            self.drowing_OBJ("../nogit_object/12140_Skull_v3_L2.obj",[10,10,10],self.judge_instance.midfin_vec(),[0,0,self.judge_instance.palm_dipth()])#40cm先に表示
            cv2.putText(self.ImgLeft_Mode,str(self.current_mode),(200,80),drowing.FONT2,1,drowing.FONT_COLOR,2)
            cv2.putText(self.ImgRight_Mode,str(self.current_mode),(200,80),drowing.FONT2,1,drowing.FONT_COLOR,2)
    
        if text_prehansig == "choice_mode_move" or text_prehansig == "choice_mode_cleck":
            if (#右目の画面の設定のところに人差し指があるなら
                self.img_pro_insname_R.point_processing(self.judge_instance.rect_trans()[8])[0] > self.window_pxl_width-100 and
                self.img_pro_insname_R.point_processing(self.judge_instance.rect_trans()[8])[1] < 100
            ):
                if text_prehansig == "choice_mode_cleck":#cleckしたなら
                    if self.wheather_merging[3] == 0:#Modeレイヤーをマージするかどうかを変更
                        self.wheather_merging[3] = 1
                    elif self.wheather_merging[3] == 1:
                        self.wheather_merging[3] = 0