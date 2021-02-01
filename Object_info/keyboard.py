#キーボードオブジェクトのjsonファイルを作るためだけのコード

import json

# {
#     [ [[x,y,z],キーの名前], [], [], ....], 一番下の暖のキー(スペースキー)
#     [                                     ], 下から二番目の段のキー
#     [                                     ],
#     [                                     ],
#     [                                     ],
#     [                                     ] ENTERキーなど
# }

keynames = [
    ["z","x","c","v","b","n","m",",",".","/"],
    ["a","s","d","f","g","h","j","k","l",";"],
    ["q","w","e","r","t","y","u","i","o","p"],
    ["1","2","3","4","5","6","7","8","9","0"],
]

dict_1={}

with open("Object_info/keyboard.json","w") as KEYBOARD_JSON_FILE:
    KEYBOARD_BUTTON = [ [-20,5,40],[20,5,40],[20,2,0],[-20,2,0] ] #ボタンの原点はボタンの下部真ん中
    KEYBOARD_SPACE = [ [-50,5,40],[50,5,40],[50,2,0],[-50,2,0] ]
    #enterはキーボード原点から 見ずらいから、隣のキーと1cm空ける
    KEYBOARD_ENTER = [ [260,50,245],[300,50,245],[300,7,55],[260,7,55] ] 

    #キーボードのボタンを描画

    #1段目 今はスペースキーのみ
    verList=[]
    horoList=[]
    keybox=[]
    for i in range(0,4):
        keybox.append([ 
            KEYBOARD_SPACE[i][0],
            KEYBOARD_SPACE[i][1],
            KEYBOARD_SPACE[i][2]
        ])
    horoList.append([keybox,"space"])
    verList.append(horoList)

    #普通のキー　2段目から5段目
    for k in range(1,5):#縦方向
        horoList=[]
        for j in range(0,10):#横方向
            keybox=[] #キーの四角
            for i in range(0,4):
                keybox.append( [ 
                    KEYBOARD_BUTTON[i][0]+j*50-225, 
                    KEYBOARD_BUTTON[i][1]+k*10+4, 
                    #z方向にはさらに手のひらの深さも足す
                    KEYBOARD_BUTTON[i][2]+k*50+5
                ] )
                
            horoList.append( [keybox, keynames[k-1][j]] )
            print([keybox, keynames[k-1][j]],"\n")
        verList.append(horoList)     

    horoList=[]
    keybox=[]
    for i in range(0,4):
        keybox.append([
            KEYBOARD_ENTER[i][0],
            KEYBOARD_ENTER[i][1],
            KEYBOARD_ENTER[i][2]
        ])
    horoList.append([keybox,"enter"])
    verList.append(horoList)

    dict_1["key"] = verList    

    json.dump(dict_1,KEYBOARD_JSON_FILE)