#画像処理のモジュール

import math

#初めから極座標で画像の位置を決めると、二つめのディスプレイで表示するとき面倒なので、これで変換
class plr_trns: #polar transformation
    def __init__(
        self,
        vertex_distance,#目の頂点と表示するディスプレイの距離
        display_width,#ディスプレイの横幅
        eye_coordinate, #眉間を0としたときの目のx座標
        ):
        self.vertex_distance = vertex_distance
        self.display_width = display_width
        self.eye_coordinate = eye_coordinate

        #高さself.VERTEX_DISTANCE、底辺DISPLAY_WIDTHの二等辺三角形を
        #半径self.VERTEX_DISTANCE、位相arctan{DISPLAY_WIDTH/ (self.VERTEX_DISTANCE/2) }
        #の扇とする
        #ディスプレイで表示できる第一証言の最大角度をもとめる 単位はラジアン
        self.max_display_angle_x = math.atan(self.display_width / (2*self.vertex_distance))
        
        self.original_position=[]
        self.slided_position_x=0.0
        self.object_coordinate_x=0.0
        self.object_coordinate_y=0.0

    def point_processing(self, ##点の位置を3Dに見えるように移動させるメソッド
        original_position,#リスト x,y,z
        ):
        #オブジェクトの座標を目の位置に合わせてずらす
        self.original_position = original_position
        self.slided_position_x = self.original_position[0] + self.eye_coordinate

        #画面に表示するx座標=水平方向角度　y座標=垂直方向角度 となる
        self.object_coordinate_x = math.atan(self.slided_position_x / self.original_position[2])
        self.object_coordinate_y = math.atan(self.original_position[1] / self.original_position[2])

        return int(self.object_coordinate_x*500),int(self.object_coordinate_y*500)
        #intにしないとcv2で描画できない
        #500はウィンドウの縦と横幅　あとでちゃんとやれるように直す
