# SmartGlass202101
## 概要
SmartGlass2020の改良版になります。<br>
こちらのmediapipe handsを使用し、手の座標を読み取っています。<br>
https://google.github.io/mediapipe/solutions/hands

## 表示方法
mediapipeから返された極座標の値をdrowing.pyに渡します。<br>
drowing.pyからhandsign_judge.pyを呼び出しジェスチャーを判断します。<br>
必要であれば直交座標のオブジェクトを呼び出します。オブジェクトの各値をimg_processing.pyで左右の目に合わせてずらし、極座標で返します。<br>
![シーケンス図](Discription/SmartGlass202101_sequence01.png)

### 手のひらの距離の測り方
handsign_judge.pyのメソッドpalm_dipthを使用しています。<br>
![palm_dipth解説](Discription/construction__handsign_judge__palm_dipth-1.png)

## キーボードの入力
第二間接の座標(x0,y0,z0)から指先の座標(x1,y1,z1)までのベクトルv=(a,b,c)は<br>
![指の第二関節から指先までのベクトル](https://latex.codecogs.com/png.latex?\&space;v&space;=&space;\left(&space;\begin{array}{ccc}&space;x1&space;-&space;x0&space;\\&space;y1&space;-&space;y0&space;\\&space;z1&space;-&space;z0&space;\end{array}&space;\right)&space;\)

よって
https://latex.codecogs.com/png.latex?\&space;\frac{x-x0}{a}&space;=&space;\frac{y-y0}{b}&space;=&space;\frac{z-z0}{c}&space;\

