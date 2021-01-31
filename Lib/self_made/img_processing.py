#画面に表示するオブジェクトを立体的に見えるように加工するモジュール

import math

class plr_trns: #polar transformation
    def __init__( #x=0はカメラ映像中心,y=0はカメラ映像上辺
        self,
        vertex_distance,#目の頂点と表示するディスプレイの距離
        display_shape,#ディスプレイの横と縦はば[mm]
        window_pxl_shape,#ディスプレイのピクセル数
        eye_coordinate, #眉間を0としたときの目のx座標 カメラでもok
    ):
        self.vertex_distance = vertex_distance
        self.display_width = display_shape[0]
        self.display_hight = display_shape[1]
        self.window_pix_width = window_pxl_shape[0]
        self.window_pix_hight = window_pxl_shape[1]
        self.eye_coordinate = eye_coordinate #目の高さが左右非対称の場合はyも変える必要があるので、その時はeye_coordinateをxとyのリストにする

        #高さself.VERTEX_DISTANCE、底辺DISPLAY_WIDTHの二等辺三角形を
        #半径self.VERTEX_DISTANCE、位相arctan{DISPLAY_WIDTH/ (self.VERTEX_DISTANCE/2) }
        #の扇とする
        #ディスプレイで表示できる横方向の最大角度をもとめる 単位はラジアン
        self.max_display_angle_x = math.atan(self.display_width / (2*self.vertex_distance))
        self.max_display_angle_y = self.max_display_angle_x * (self.window_pix_hight/self.window_pix_width)
        
        self.slided_position_x=0.0
        self.slided_position_y=0.0
        self.object_coordinate_x=0.0
        self.object_coordinate_y=0.0

    def point_processing(##点の位置を3Dに見えるように移動させるメソッド
        self, 
        original_position,#リスト[x,y,z] 直交座標
    ):
        #オブジェクトの座標を目の位置に合わせてずらす
        self.slided_position_x = (
            original_position[0] #原点をずらした方向と反対側に値が変わる
            - self.eye_coordinate #目の位置に合わせて原点を変更
        )

        self.slided_position_y = original_position[1]

        #画面に表示するx座標=水平方向角度　y座標=垂直方向角度 となる
        self.object_coordinate_x = (
            math.atan(self.slided_position_x / original_position[2]) / self.max_display_angle_x
            #↑角度/表示できる最大角度 画面の端から端までを1としていくつか
            * self.window_pix_width
            + self.window_pix_width/2 #原点を画面中央に  
        )
        
        self.object_coordinate_y = ( 
            #↓このままだとyが下方向になるので-1を掛ける
            -math.atan(self.slided_position_y / original_position[2]) /self.max_display_angle_y
            * self.window_pix_hight
            + self.window_pix_hight /2 
        )

        print(
            "\n\nimg_processingログ",
            "\n移動前の座標",original_position,
            "\n横に何度/横方向最大表示角度",math.atan(self.slided_position_x / original_position[2]) / self.max_display_angle_x,
            "\n縦に何度/縦方向最大表示角度",math.atan(self.slided_position_y / original_position[2]) /self.max_display_angle_y,
            "\n移動後の座標",int(self.object_coordinate_x),int(self.object_coordinate_y)
        )

        return int(self.object_coordinate_x),int(self.object_coordinate_y)
        #intにしないとcv2で描画できない