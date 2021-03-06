import cv2
import numpy as np
import json
import math
import traceback
from PIL import Image

#cv2で描画するときはアルファ値も指定しないといけないので注意

class drowing:#モードの記述や画面クリアなどで、相対座標ではなく、絶対座標から指定してしまっている imgproccesingとか使って相対座標で描けるように
    FONT1 = cv2.FONT_HERSHEY_COMPLEX
    FONT2 = cv2.FONT_HERSHEY_COMPLEX_SMALL
    FONT_COLOR = [0,0,0,255]
    CLEAR_COLOR = [255,255,255,255]
    ALPHA_COLOR = [0,0,0,0]
    CHOICE_COLOR = [0,255,0,255]
    KEYBOARD_BASE = [ [-250,50,250],[300,50,250],[300,0,0],[-250,0,0] ]#keyboardの大きさ[mm]
    KEYBOARD_BASE_COLOR = [0,0,0,255]
    KEYBOARD_BUTTON_COLOR = [255,255,0,255]
    NOMATERIAL_COLOR = [255,0,0,255]#オブジェクトを表示するとき、表示するmaterialが指定されていない時の色

    def __init__(self,Leftlayers=None,Rightlayers=None,judgeInstance=None,imgProInstance_L=None,imgProInstance_R=None,window_pxl_shape=[[],[]],wheather_merging_layer=[],timeMesureInstance=None):
        self.ImgLeft_Base = Leftlayers[0]#レイヤーのインデックスが大きいほど手前に idxとレイヤーの前後関係はhandtracking.pyの合成順で定義
        self.ImgRight_Base = Rightlayers[0]
        self.ImgLeft_ObjectLayers = Leftlayers[1:-3]
        self.ImgRight_ObjectLayers = Rightlayers[1:-3]
        self.ImgLeft_Keyboard = Leftlayers[-3]
        self.ImgRight_Keyboard = Rightlayers[-3]
        self.ImgLeft_Mode = Leftlayers[-2]
        self.ImgRight_Mode = Rightlayers[-2]
        self.ImgLeft_Hand = Leftlayers[-1]
        self.ImgRight_Hand = Rightlayers[-1]

        self.judge_instance = judgeInstance #handsign_judgeのインスタンス
        self.imgProInstance_L = imgProInstance_L #左目のimg_processingのインスタンス
        self.imgProInstance_R = imgProInstance_R #右目のimg_processingのインスタンス

        self.timeMeasureInstance = timeMesureInstance#時間を測るインスタンス 間違えて呼び出すとカウントがスタートしてバグの元になるので注意

        self.window_pxl_width = window_pxl_shape[0]#表示する画像の幅
        self.window_pxl_hight = window_pxl_shape[1]

        self.wheather_merging_layer = wheather_merging_layer #それぞれのlayerをマージするかどうか

        self.palm_dipth_info = None

        self.object_position_infos={} #オブジェクトの座標 手のひらの横幅を基準に考える

        self.before_pro_object = [] #加工前のオブジェクトの頂点の座標のリスト
        self.eyeL_ofter_pro_object = [] #加工後のオブジェクトの頂点の座標のリスト
        self.eyeR_ofter_pro_object = []

        self.present_HandSignText = "not"
        self.HandSignText_backup = "not"
        self.current_mode = []#現在有効なモード

        #readOBJ
        self.readOBJ_path_backup=None
        self.readOBJ_result_backup={}#keyがpathの辞書
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

        #choiceObject
        self.objectCriteriaPositions = {} #{0:[x0,y0,z0],1:[x1,y1,z1],2:[],..}　Criteria=基準,目安 self.ImgRignt_objectLayersのインデックス番号と同じkey名
        #↑要は 当たり判定の立方体 の中心の点

        #drowing_keyboard
        self.LOADED_KEYBOARD_JSON = None
        self.key_position = None
        self.slided_key_positions_ver = []#縦方向に区切るリスト slided_key_positionに代入するときしか使わない
        self.slided_key_positions = []

        #drowing_hand 関数からいじれるようにしたかったので、クラス変数ではなくインスタンス変数にした
        self.hand_landmarks_color=[255,0,0,255]

        #drowing_3Dview
        self.COResult_ret=None

        
    #画面クリア
    def imgReset(self,layerName,resetRange="all",imgReset_whatLayer=0):
        if layerName == "base":
            self.imgReset_layer = [self.ImgLeft_Base,self.ImgRight_Base]
            if resetRange == "all":
                cv2.rectangle(self.imgReset_layer[0],(0,0),(500,500),drowing.CLEAR_COLOR,thickness=-1)
                cv2.rectangle(self.imgReset_layer[1],(0,0),(500,500),drowing.CLEAR_COLOR,thickness=-1)
            elif resetRange == "main":#テキストを表示しない場所
                cv2.fillConvexPoly(self.imgReset_layer[0],np.array([
                    (0,0),(200,0),(200,50),(200,100),(500,100),(500,500),(0,500)
                ]),drowing.CLEAR_COLOR)
                cv2.fillConvexPoly(self.imgReset_layer[1],np.array([
                    (0,0),(0,50),(200,50),(200,100),(500,100),(500,500),(0,500)
                ]),drowing.CLEAR_COLOR)

        else:
            if layerName == "object":
                self.imgReset_layer = [self.ImgLeft_ObjectLayers[imgReset_whatLayer],self.ImgRight_ObjectLayers[imgReset_whatLayer]]
            elif layerName == "mode":
                self.imgReset_layer = [self.ImgLeft_Mode,self.ImgRight_Mode]
            elif layerName == "hand":
                self.imgReset_layer = [self.ImgLeft_Hand,self.ImgRight_Hand]
            elif layerName == "keyboard":
                self.imgReset_layer = [self.ImgLeft_Keyboard,self.ImgRight_Keyboard]
            else:
                try:
                    raise Exception
                except:
                    traceback.print_exc()
                    print(layerName,"を受け取りました。リセットする画像が正しく指定されていません")
            #baseでなければ透明で塗りつぶし
            if resetRange == "all":
                cv2.rectangle(self.imgReset_layer[0],(0,0),(500,500),drowing.ALPHA_COLOR,thickness=-1)
                cv2.rectangle(self.imgReset_layer[1],(0,0),(500,500),drowing.ALPHA_COLOR,thickness=-1)
        
            elif resetRange == "prehansig":
                #透明の長方形で塗りつぶし
                cv2.rectangle(self.imgReset_layer[0],(200,0),(500,50),drowing.ALPHA_COLOR,thickness=-1)
                cv2.rectangle(self.imgReset_layer[1],(200,0),(500,50),drowing.ALPHA_COLOR,thickness=-1)
                
            elif resetRange == "current_mode":
                cv2.rectangle(self.imgReset_layer[0],(200,50),(500,100),drowing.ALPHA_COLOR,thickness=-1)
                cv2.rectangle(self.imgReset_layer[1],(200,50),(500,100),drowing.ALPHA_COLOR,thickness=-1)
            
            elif resetRange == "main":#テキストを表示しない場所
                cv2.fillConvexPoly(self.imgReset_layer[0],np.array([
                    (0,0),(200,0),(200,50),(200,100),(500,100),(500,500),(0,500)
                ]),drowing.ALPHA_COLOR)
                cv2.fillConvexPoly(self.imgReset_layer[1],np.array([
                    (0,0),(0,50),(200,50),(200,100),(500,100),(500,500),(0,500)
                ]),drowing.ALPHA_COLOR)

    #ぐるぐる(進捗インジゲータ)をobjectlayersの一番上のレイヤーに表示
    def drowProgressIndicator(self,progress=float,whatObjectLayerNum=int):#0.0<=progress<=1.0
        cv2.ellipse(
            self.ImgLeft_ObjectLayers[whatObjectLayerNum],
            (int(self.window_pxl_width/2),int(self.window_pxl_hight/2)),
            (int(self.window_pxl_width/20),int(self.window_pxl_hight/20)),
            270,
            0,
            -int(progress*360),
            [55+int(progress*200),455-int(progress*200),0,125],
            5,
            cv2.LINE_AA
        )
        cv2.ellipse(
            self.ImgRight_ObjectLayers[whatObjectLayerNum],
            (int(self.window_pxl_width/2),int(self.window_pxl_hight/2)),
            (int(self.window_pxl_width/20),int(self.window_pxl_hight/20)),
            270,
            0,
            -int(progress*360),
            [55+int(progress*200),455-int(progress*200),0,125],
            5,
            cv2.LINE_AA
        )

    #objファイルをリストにする
    def readOBJ(self,path):
        #すでに読み込まれていたものであれば 
        if path in self.readOBJ_result_backup:#self.readOBJ_result_backup.key()と同じ意味
            return self.readOBJ_result_backup[path]
        self.vertices = []
        self.uvs = []
        self.normals = []
        self.faceVertIDs = []
        self.uvIDs = []
        self.normalIDs = []
        self.vertexColor = []
        self.readOBJ_groupName = "nanashi"#groupがobjファイルに記載されていない場合は、これがkeyになる
        self.mtlName = None
        self.readOBJ_result_backup[path] = {}#{ path:{mtllib:materialファイル名 , groupName1:[] , groupName2:[] , .... } }
        for line in open(path, "r"):
            vals = line.split()
            if len(vals) == 0:
                continue
            elif vals[0] == "v":
                v = vals[1:4]
                self.vertices.append(v)
                if len(vals) == 7:
                    vc = vals[4:7]
                    self.vertexColors.append(vc)
                self.numVertices += 1
            elif vals[0] == "vt":
                vt = vals[1:3]
                self.uvs.append(vt)
                self.numUVs += 1
            elif vals[0] == "vn":
                vn = vals[1:4]
                self.normals.append(vn)
                self.numNormals += 1
            elif vals[0] == "f":
                fvID = []
                uvID = []
                nvID = []
                for f in vals[1:]:
                    w = f.split("/")
                    if self.numVertices > 0:
                        fvID.append(int(w[0])-1)#IDの値を一つ下げて、0から始まるようにしている
                    elif self.numUVs > 0:
                        uvID.append(int(w[1])-1)
                    elif self.numNormals > 0:
                        nvID.append(int(w[2])-1)
                self.faceVertIDs.append(fvID)
                self.uvIDs.append(uvID)
                self.normalIDs.append(nvID)
                self.numFaces += 1

            elif vals[0] == "g":#グループなら
                #まず古いgroupNameで辞書に登録してから
                self.readOBJ_result_backup[path][self.readOBJ_groupName] =[ self.vertices, self.uvs, self.normals, self.faceVertIDs, self.uvIDs, self.normalIDs, self.vertexColors, self.mtlName ]
                #key名を変える
                self.readOBJ_groupName = vals[1]
                #新しいkey名(group名)で辞書を作る
                self.readOBJ_result_backup[path][self.readOBJ_groupName] = {}
                self.vertices = []
                self.uvs = []
                self.normals = []
                self.faceVertIDs = []
                self.uvIDs = []
                self.normalIDs = []
                self.vertexColor = []
            elif vals[0] == "usemtl":#material名なら
                self.mtlName = vals[1]
            elif vals[0] == "mtllib":#materialファイル名なら
                self.readOBJ_result_backup[path]["mtllib"] = vals[1]        
        #辞書に登録しきれていない、最後のグループを辞書に登録
        self.readOBJ_result_backup[path][self.readOBJ_groupName] =[ self.vertices, self.uvs, self.normals, self.faceVertIDs, self.uvIDs, self.normalIDs, self.vertexColors, self.mtlName ]
        return self.readOBJ_result_backup[path]

    def readMTL(self,path):
        self.readMTL_materialName = "nanashi"
        self.materlalInfos={self.readMTL_materialName:{}}#{material名1:{"Kd":[RGB(0.0~1.0)], "":[], ...}, material名2:{"Kd":[], ...}, ...}
        for line in open(path,"r"):#このやり方でも開ける
            vals = line.split()
            if len(vals) == 0:
                continue
            if vals[0] == "Kd":#ディフューズ(拡散反射)なら
                self.materlalInfos[self.readMTL_materialName]["Kd"] = vals[1:]
            elif vals[0] == "newmtl":#新しいmaterialなら
                self.readMTL_materialName = vals[1]#material名を変えて
                self.materlalInfos[self.readMTL_materialName] = {}#新しい辞書を作成
            else :#他にもいっぱいあるけど、とりあえず
                continue
        return self.materlalInfos

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
            self.eyeL_ofter_pro_object.append( self.imgProInstance_L.point_processing(self.before_pro_object) )
            self.eyeR_ofter_pro_object.append( self.imgProInstance_R.point_processing(self.before_pro_object) )
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
                        self.eyeL_ofter_pro_object.append( self.imgProInstance_L.point_processing(self.before_pro_object) )
                        self.eyeR_ofter_pro_object.append( self.imgProInstance_R.point_processing(self.before_pro_object) )
                    if (not None in self.eyeL_ofter_pro_object) and (not None in self.eyeR_ofter_pro_object):#描画距離内なら
                        cv2.fillConvexPoly(self.ImgLeft_Keyboard,np.array(self.eyeL_ofter_pro_object),drowing.KEYBOARD_BUTTON_COLOR)#drowing.KEYBOARD_BUTTON_COLOR)
                        cv2.fillConvexPoly(self.ImgRight_Keyboard,np.array(self.eyeR_ofter_pro_object),drowing.KEYBOARD_BUTTON_COLOR)

                    self.slided_key_positions_ver.append([self.slided_key_position_keyrect,keybox_and_name[1]])#ずらしたキーボードの座標と名前を記録
                self.slided_key_positions.append(self.slided_key_positions_ver)


    def keybaord_typing(self):
        self.typing_mat_2 = self.judge_instance.fin_vec_equation(3)#押したかどうか判別する行列の2行目まで(指の行列)と答えを取得
        #テスト用　人差し指とキーボードのベースの交点
        if (
            self.judge_instance.rect_trans()[(1+1)*4-2][1] < self.slided_key_positions[4][0][0][0][1] and self.judge_instance.rect_trans()[(1+1)*4][1] > self.slided_key_positions[0][0][0][2][1] and 
            self.judge_instance.rect_trans()[(1+1)*4-2][2] < self.slided_key_positions[4][0][0][0][2] and self.judge_instance.rect_trans()[(1+1)*4][2] > self.slided_key_positions[0][0][0][2][2]  and 
            self.judge_instance.rect_trans()[(1+1)*4-2][0] < self.slided_key_positions[1][9][0][0][0] and self.judge_instance.rect_trans()[(1+1)*4][0] > self.slided_key_positions[1][0][0][0][0]
        ):
            print("人差し指キーボードの範囲内には入ってる 交点は",self.judge_instance.rect_trans()[(1+1)*4-2])
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
        #↓交点を標準出力
        #print(
        #    "人差し指の向きは",self.typing_mat_2[1][0],"\n",
        #    "x",self.judge_instance.rect_trans()[(1+1)*4-2][0] ,self.slided_key_positions[1][9][0][0][0], self.slided_key_positions[1][0][0][0][0],"\n",
        #    "y",self.judge_instance.rect_trans()[(1+1)*4-2][1] , self.slided_key_positions[4][0][0][0][1],self.slided_key_positions[0][0][0][2][1],"\n",
        #    "z",self.judge_instance.rect_trans()[(1+1)*4-2][2] ,self.slided_key_positions[4][0][0][0][2], self.slided_key_positions[0][0][0][2][2],"\n",
        #    "スペースキーの高さは",self.slided_key_positions[0][0][0][0][1],"\n"
        #    "スペースキーの平面との交点は\n",
        #    self.test_space_cross,"\n"
        #)
        #交点を黒で表示
        cv2.circle(self.ImgLeft_Hand, self.imgProInstance_L.point_processing([
            self.test_space_cross[0,0],self.test_space_cross[1,0],self.test_space_cross[2,0]
        ]),30,(0,0,0,255),5)
        cv2.circle(self.ImgRight_Hand, self.imgProInstance_R.point_processing([
            self.test_space_cross[0,0],self.test_space_cross[1,0],self.test_space_cross[2,0]
        ]),30,(0,0,0,255),5)
        #人差し指の直線を緑で表示
        cv2.line(
            self.ImgLeft_Hand, 
            self.imgProInstance_L.point_processing(
                self.judge_instance.rect_trans()[6]
            ),
            self.imgProInstance_L.point_processing(
                self.judge_instance.rect_trans()[8]
            ),
            (0,255,0,255),
            3
        )
        cv2.line(
            self.ImgRight_Hand, 
            self.imgProInstance_R.point_processing(
                self.judge_instance.rect_trans()[6]
            ),
            self.imgProInstance_L.point_processing(
                self.judge_instance.rect_trans()[8]
            ),
            (0,255,0,255),
            3
        )
        if (
            self.imgProInstance_L.point_processing([self.test_space_cross[0,0],self.test_space_cross[1,0],self.test_space_cross[2,0]])
        ):
            if (
                self.imgProInstance_L.point_processing([self.test_space_cross[0,0],self.test_space_cross[1,0],self.test_space_cross[2,0]])[0] > 100 and 
                self.imgProInstance_L.point_processing([self.test_space_cross[0,0],self.test_space_cross[1,0],self.test_space_cross[2,0]])[0] < 400 and
                self.imgProInstance_L.point_processing([self.test_space_cross[0,0],self.test_space_cross[1,0],self.test_space_cross[2,0]])[1] > 100 and
                self.imgProInstance_L.point_processing([self.test_space_cross[0,0],self.test_space_cross[1,0],self.test_space_cross[2,0]])[1] < 400
            ):
                print("交点が画面の中央付近！ 交点は",self.test_space_cross[0,0],self.test_space_cross[1,0],self.test_space_cross[2,0])
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
                    #cross_pointの中身は [ [x 0 0],[y 0 0],[z 0 0] ]

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

    #mgnification:拡大 rotation:回転 taranslation:平行移動
    #mtlFolderPathはobjファイルで指定している、mtlファイルのpath whatLayerNumは何番目のレイヤーか(0~)
    def drowingOBJ(self,path,whatLayerNum=0,magnification=[1,1,1],rotation=[[1,0,0],[0,1,0],[0,0,1]],translation=[0,0,0],targets=["vertex"],mtlFolderPath="./Objct_info/"):
        self.drowingOBJ_ObjFile = self.readOBJ(path)
        self.drowingOBJ_materialFileName = self.drowingOBJ_ObjFile["mtllib"]#materialファイル名
        self.drowingOBJ_materialS = self.readMTL(mtlFolderPath+self.drowingOBJ_materialFileName)#materialファイルに書かれたmaterialのリスト
        for groupName in self.drowingOBJ_ObjFile:#各グループごとに描画する
            if groupName == "mtllib":#materialファイル名なら、
                continue
            self.obj_vertices = self.drowingOBJ_ObjFile[groupName][0]
            self.vertex_num = 0#カウント用変数
            self.processed_obj_vertices_position = [ {},{} ] #imgprocessing.pyで加工後の左右の画面上の頂点の座標のリスト
            for obj_vertex in self.obj_vertices:
                obj_vertex=[#代入後のobj_vertexを別の変数にする方が、拡張しやすいかもしれない ただ、processing.pyとobj_vertexの移動を同時にやったらマジでこんがらがるからやめた方がいい
                    ( rotation[0][0]*float(obj_vertex[0]) + rotation[0][1]*float(obj_vertex[1]) + rotation[0][2]*float(obj_vertex[2]) )*magnification[0] +translation[0],
                    ( rotation[1][0]*float(obj_vertex[0]) + rotation[1][1]*float(obj_vertex[1]) + rotation[1][2]*float(obj_vertex[2]) )*magnification[1] +translation[1],
                    ( rotation[2][0]*float(obj_vertex[0]) + rotation[2][1]*float(obj_vertex[1]) + rotation[2][2]*float(obj_vertex[2]) )*magnification[2] +translation[2],
                ]
                if self.imgProInstance_L.point_processing(obj_vertex) and self.imgProInstance_R.point_processing(obj_vertex):#この真偽値で描画範囲内か判断する方法って良くないかもしれない
                    self.processed_obj_vertices_position[0][self.vertex_num] = self.imgProInstance_L.point_processing(obj_vertex)
                    self.processed_obj_vertices_position[1][self.vertex_num] = self.imgProInstance_R.point_processing(obj_vertex)
                    #targetにvertexが指定されているなら、この時一緒に頂点を描く
                    if ("vertex" in targets) and self.processed_obj_vertices_position[0][self.vertex_num] and self.processed_obj_vertices_position[1][self.vertex_num]: 
                        cv2.circle(self.ImgLeft_ObjectLayers[whatLayerNum], self.processed_obj_vertices_position[0][self.vertex_num] ,1,(int(obj_vertex[2]*0.5), int(255-obj_vertex[2]*0.5), int(obj_vertex[2]*0.5) ))
                        cv2.circle(self.ImgRight_ObjectLayers[whatLayerNum], self.processed_obj_vertices_position[1][self.vertex_num] ,1,(int(obj_vertex[2]*0.5), int(255-obj_vertex[2]*0.5), int(obj_vertex[2]*0.5) ))
                self.vertex_num += 1
                
            #面
            if "surface" in targets:
                obj_surfaceS = self.drowingOBJ_ObjFile[groupName][3]
                if self.drowingOBJ_ObjFile[groupName][-1]:#material情報があるなら、読み込む
                    self.drowingOBJ_material = self.drowingOBJ_materialS[ self.drowingOBJ_ObjFile[groupName][-1] ]#この時点では "Kd":[0.51~,0.44~,0.31~]
                    self.drowingOBJ_material = [int( float(self.drowingOBJ_material["Kd"][0]) *255),int( float(self.drowingOBJ_material["Kd"][1]) *255),int( float(self.drowingOBJ_material["Kd"][2]) *255),255]#アルファチャンネルを読みとれるのであれば、Aを変えた方がいい
                else:#ないなら、NOMATERIAL_COLORにする
                    self.drowingOBJ_material = drowing.NOMATERIAL_COLOR
                for obj_surface_vertices_IDs in obj_surfaceS:
                    self.drowingOBJ_processed_CurrentSurfaceVerticesPositions_L = []
                    self.drowingOBJ_processed_CurrentSurfaceVerticesPositions_R = []
                    #全ての頂点が描画範囲内なら
                    if set(obj_surface_vertices_IDs) <= set(list( self.processed_obj_vertices_position[0].keys() )):#ディスプレイ上の座標をsetに変換するのはfor文の外に出した方がいいかも　遅いから
                        for current_surface_vertices_ID in obj_surface_vertices_IDs:
                            #ディスプレイ上の座標をリストに格納
                            self.drowingOBJ_processed_CurrentSurfaceVerticesPositions_L.append( self.processed_obj_vertices_position[0][current_surface_vertices_ID] )
                            self.drowingOBJ_processed_CurrentSurfaceVerticesPositions_R.append( self.processed_obj_vertices_position[1][current_surface_vertices_ID] )
                        cv2.fillConvexPoly(
                            self.ImgLeft_ObjectLayers[whatLayerNum],
                            np.array(self.drowingOBJ_processed_CurrentSurfaceVerticesPositions_L),
                            self.drowingOBJ_material#ここのaの値をいい感じに調整して、面が重なると色が濃くなるようにしてもいいかも
                        )
                        cv2.fillConvexPoly(
                            self.ImgRight_ObjectLayers[whatLayerNum],
                            np.array(self.drowingOBJ_processed_CurrentSurfaceVerticesPositions_R),
                            self.drowingOBJ_material
                        )

    #positionとobjectを照合してpositionと一致するself.objectLayersのインデックス番号を返す 戻り値の1番目は一致するものがあったかどうか
    def choiceObject(self,position=list,hitRange=50):
        for objectLayerNum in self.objectCriteriaPositions:
            if (
                abs(self.objectCriteriaPositions[objectLayerNum][0] - position[0]) < hitRange and
                abs(self.objectCriteriaPositions[objectLayerNum][1] - position[1]) < hitRange and
                abs(self.objectCriteriaPositions[objectLayerNum][2] - position[2]) < hitRange
            ):
                return True,objectLayerNum
        return None,None

    #手を書く 現時点では点のみ
    def drowing_hand_landmarks(self):
        self.eyeL_ofter_pro_object=[]
        self.eyeR_ofter_pro_object=[]
        for transd_lndmrk in self.judge_instance.rect_trans():
            if self.imgProInstance_L.point_processing(transd_lndmrk) and self.imgProInstance_R.point_processing(transd_lndmrk):#描画距離内なら
                cv2.circle(self.ImgLeft_Hand, self.imgProInstance_L.point_processing(transd_lndmrk) ,3,self.hand_landmarks_color,2)
                cv2.circle(self.ImgRight_Hand, self.imgProInstance_R.point_processing(transd_lndmrk) ,3,self.hand_landmarks_color,2)

    #メインの関数 ここでは「各関数の呼び出し」と「関数を作るほどではない処理」のみ行う
    def drowing_3Dview(self,mode=None): 
        self.present_HandSignText=self.judge_instance.handsignText()#present=現在の
        self.imgReset("base","all")

        if mode == "drowing_hand":
            self.imgReset("hand","all")
            self.drowing_hand_landmarks()

        if self.HandSignText_backup != self.present_HandSignText: #1つ前のself.present_HandSignTextと違うなら modeレイヤーを上書き
            self.imgReset("mode","prehansig")
            self.HandSignText_backup = self.present_HandSignText
            cv2.putText(self.ImgLeft_Mode,self.present_HandSignText,(200,40),drowing.FONT1,1,drowing.FONT_COLOR,2)
            cv2.putText(self.ImgRight_Mode,self.present_HandSignText,(200,40),drowing.FONT1,1,drowing.FONT_COLOR,2)

        if self.present_HandSignText == "keyboard_open":
            if not "keyboard" in self.current_mode:
                self.imgReset("mode","current_mode")
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
        
        #self.drowProgressIndicatorの引き数whatLayerNum と self.drowingOBJの引き数whatLayerNum と self.objectCriteriaPositionsのキー をここでは0としているが、将来的には自動で空いているlayerを指定するようにしたい
        if self.present_HandSignText == "shortcut_4_wait":
            self.drowProgressIndicator( self.timeMeasureInstance.targetCount("shortcut_4")/2, whatObjectLayerNum=0 )
        elif self.present_HandSignText == "shortcut_4":
            if not "3Dobject" in self.current_mode:
                self.imgReset("object")
                self.drowingOBJ("./Object_info/semicon_01/semicon_01.obj", 0, magnification=[100,100,100],translation=self.judge_instance.rect_trans()[5],targets=["surface"],mtlFolderPath="./Object_info/semicon_01/")
                self.objectCriteriaPositions[0]=self.judge_instance.rect_trans()[5]
                self.imgReset("mode")
                self.current_mode.append("3Dobject")
                cv2.putText(self.ImgLeft_Mode,str(self.current_mode),(200,80),drowing.FONT2,1,drowing.FONT_COLOR,2)
                cv2.putText(self.ImgRight_Mode,str(self.current_mode),(200,80),drowing.FONT2,1,drowing.FONT_COLOR,2)

        elif self.present_HandSignText == "3D_tranceform":
            #フレミングの法則の形にlandmardを線でつなぐ オブジェクトを表示しているときだけ線でつないだ方がいいかも
            cv2.line(
                self.ImgLeft_Hand,
                self.imgProInstance_L.point_processing(self.judge_instance.rect_trans()[4]),
                self.imgProInstance_L.point_processing(self.judge_instance.rect_trans()[5]),
                drowing.CHOICE_COLOR,
                3,
            )
            cv2.line(
                self.ImgLeft_Hand,
                self.imgProInstance_L.point_processing(self.judge_instance.rect_trans()[8]),
                self.imgProInstance_L.point_processing(self.judge_instance.rect_trans()[5]),
                drowing.CHOICE_COLOR,
                3,
            )
            cv2.line(
                self.ImgLeft_Hand,
                self.imgProInstance_L.point_processing(self.judge_instance.rect_trans()[12]),
                self.imgProInstance_L.point_processing(self.judge_instance.rect_trans()[5]),
                drowing.CHOICE_COLOR,
                3,
            )
            cv2.line(
                self.ImgRight_Hand,
                self.imgProInstance_R.point_processing(self.judge_instance.rect_trans()[4]),
                self.imgProInstance_R.point_processing(self.judge_instance.rect_trans()[5]),
                drowing.CHOICE_COLOR,
                3,
            )
            cv2.line(
                self.ImgRight_Hand,
                self.imgProInstance_R.point_processing(self.judge_instance.rect_trans()[8]),
                self.imgProInstance_R.point_processing(self.judge_instance.rect_trans()[5]),
                drowing.CHOICE_COLOR,
                3,
            )
            cv2.line(
                self.ImgRight_Hand,
                self.imgProInstance_R.point_processing(self.judge_instance.rect_trans()[12]),
                self.imgProInstance_R.point_processing(self.judge_instance.rect_trans()[5]),
                drowing.CHOICE_COLOR,
                3,
            )
            if ("3Dobject" in self.current_mode) and self.COResult_ret:#オブジェクトを表示しており、選択しているオブジェクトがあるなら
                self.imgReset("object")
                self.imgReset("mode")
                self.current_mode.append("3Dobject")
                self.objectCriteriaPositions[self.COResult_num]=self.judge_instance.rect_trans()[5]
                #選択したobjectを変えるように
                self.drowingOBJ(
                    path="./Object_info/semicon_01/semicon_01.obj",
                    whatLayerNum=self.choiced_objectLayerNum,
                    magnification=[100,100,100],
                    rotation=[ [0,-self.judge_instance.midfin_vec()[2],self.judge_instance.midfin_vec()[1] ],[ self.judge_instance.midfin_vec()[2],0,-self.judge_instance.midfin_vec()[0] ],[ -self.judge_instance.midfin_vec()[1],self.judge_instance.midfin_vec()[0],0 ] ],
                    translation=self.judge_instance.rect_trans()[5],#人差し指の付け根を基準にして表示
                    targets=["vertex","surface"],
                    mtlFolderPath="./Object_info/semicon_01/",
                )
                cv2.putText(self.ImgLeft_Mode,str(self.current_mode),(200,80),drowing.FONT2,1,drowing.FONT_COLOR,2)
                cv2.putText(self.ImgRight_Mode,str(self.current_mode),(200,80),drowing.FONT2,1,drowing.FONT_COLOR,2)
            
    
        elif self.present_HandSignText == "choice_mode_move" or self.present_HandSignText == "choice_mode_cleck":
            cv2.circle(self.ImgLeft_Hand,self.imgProInstance_L.point_processing(self.judge_instance.rect_trans()[8]),10,drowing.CHOICE_COLOR,3)
            cv2.circle(self.ImgRight_Hand,self.imgProInstance_R.point_processing(self.judge_instance.rect_trans()[8]),10,drowing.CHOICE_COLOR,3)
            if self.present_HandSignText == "choice_mode_cleck":
                cv2.circle(self.ImgLeft_Hand,self.imgProInstance_L.point_processing(self.judge_instance.rect_trans()[8]),20,drowing.CHOICE_COLOR,4)
                cv2.circle(self.ImgRight_Hand,self.imgProInstance_R.point_processing(self.judge_instance.rect_trans()[8]),20,drowing.CHOICE_COLOR,4)
                if (#右目の画面の設定のところに人差し指があるなら
                    self.imgProInstance_R.point_processing(self.judge_instance.rect_trans()[8])[0] > self.window_pxl_width-100 and
                    self.imgProInstance_R.point_processing(self.judge_instance.rect_trans()[8])[1] < 100
                ):
                    if self.wheather_merging_layer[-2] == 0:#Modeレイヤーをマージするかどうかを変更
                        self.wheather_merging_layer[-2] = 1
                    elif self.wheather_merging_layer[-2] == 1:
                        self.wheather_merging_layer[-2] = 0
                else:
                    self.COResult_ret,self.COResult_num=self.choiceObject(self.judge_instance.rect_trans()[8],100)
                    if self.COResult_ret:#人差し指の位置が各オブジェクトの基準点と一致する(誤差±50mm)か調べる
                        self.choiced_objectLayerNum = self.COResult_num
                        cv2.circle(self.ImgRight_Hand,self.imgProInstance_R.point_processing(self.objectCriteriaPositions[self.COResult_num]),30,[0,0,255,255],2)
                        cv2.circle(self.ImgLeft_Hand,self.imgProInstance_L.point_processing(self.objectCriteriaPositions[self.COResult_num]),30,[0,0,255,255],2)
                    else:#一致するものがなければNoneを代入しなおし
                        self.choiced_objectLayerNum = None
    
        elif self.present_HandSignText == "sidewayspalm" and ("keyboard" in self.current_mode):
            self.current_mode.pop(self.current_mode.index("keyboard"))#current_modeからkeyboardを削除
            self.imgReset("keyboard","all")