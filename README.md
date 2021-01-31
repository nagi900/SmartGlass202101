# SmartGlass202101
## 概要
SmartGlass2020の改良版になります。
こちらのmediapipe handsを使用し、手の座標を読み取っています。
https://google.github.io/mediapipe/solutions/hands

## 表示方法
mediapipeから返された極座標の値をdrowing.pyに渡します。
drowing.pyからhandsign_judge.pyを呼び出しジェスチャーを判断します。
必要であれば直交座標のオブジェクトを呼び出します。オブジェクトの各値をimg_processing.pyで左右の目に合わせてずらし、極座標で返します。
![シーケンス図](Discription/SmartGlass202101_sequence01.png)

### 手のひらの距離の測り方
handsign_judge.pyのメソッドpalm_dipthを使用しています。
![palm_dipth解説](Discription/SmartGlass202101_sequence01.png)
