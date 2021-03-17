#このコードではmaterialは指定できません。(20210316)
#直接objファイルを触ってmaterialの指定をしました。(20210316)
#書けるように変更してください

#Siの半導体の2*2*2の立方体の中の原子
atom_pos = [
    #八隅の原子
    [1.0, 1.0, 1.0],
    [1.0, -1.0, 1.0],
    [1.0, 1.0, -1.0],
    [1.0, -1.0, -1.0],
    [-1.0, 1.0, 1.0],
    [-1.0, 1.0, -1.0],
    [-1.0, -1.0, 1.0],
    [-1.0, -1.0, -1.0],
    #各面の中心の原子
    [1.0, 0, 0],
    [0, 1.0, 0],
    [0, 0, 1.0],
    [-1.0, 0, 0],
    [0, -1.0, 0],
    [0, 0, 1-.0],
    #立方体の中の原子
    [0.5, 0.5, 0.5],
    [0.5, -0.5, -0.5],
    [-0.5, -0.5, 0.5],
    [-0.5, 0.5, -0.5],
]
import numpy as np
import math
semi_vS = []
print(math.cos(math.pi/6))
for semi in atom_pos:
    semi_v = []
    semi_v.append([str(semi[0]),str(semi[1] + 0.1),str(semi[2])]) 
    for t in range(6):#真横(y軸に垂直)に見たとき、正六角形になるように
        semi_v.append( [ str(semi[0]+math.cos(math.pi/6*t)*0.1), str(semi[1]+0.05), str(semi[2]+math.sin(math.pi/6*t)*0.1) ] )
    for t in range(6):
        semi_v.append( [ str(semi[0]+math.cos(math.pi/6*t)*0.1), str(semi[1]-0.05), str(semi[2]+math.sin(math.pi/6*t)*0.1) ] )
    semi_v.append([str(semi[0]),str(semi[1]-0.1),str(semi[2])]) 
    semi_vS.append(semi_v)
with open("./object_info/semicon_01/semicon_01.obj","w") as f:
    #頂点
    for wr_semi_v in semi_vS:
        for v in wr_semi_v:
            f.write("v ")
            for v_pos in v:
                f.write(v_pos)
                f.write(" ")
            f.write("\n")
    #辺
    i=0
    for semi_v in semi_vS:#個数を調べるのを省略するためだけ
        for j in range(5):#上の六つの三角形
            f.write(f"f {i*14+1} {i*14+j+2} {i*14+j+3} \n")
        f.write(f"f {i*14+1} {i*14+7} {i*14+2} \n")
        #drowしたら変な形に面がついてしまったので、テスト
        for j in range(5):#側面 回転方向統一しないと、ちゃんと描画できないことがある
            f.write(f"f {i*14+j+2} {i*14+j+8} {i*14+j+9} {i*14+j+3}\n")
        f.write(f"f {i*14+2} {i*14+8} {i*14+13} {i*14+7}\n")
        for j in range(5):#下の六つの三角形
            f.write(f"f {i*14+14} {i*14+j+8} {i*14+j+9} \n")
        f.write(f"f {i*14+14} {i*14+8} {i*14+13}\n")
        i +=1