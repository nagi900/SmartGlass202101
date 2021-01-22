import cv2
import numpy as np
import Lib.self_made.handsign_judge #相対パス

class drowing:
    font = cv2.FONT_HERSHEY_SIMPLEX
    

    def __init__(self,default,Img1=None,Img2=None,Img1_name=None,Img2_name=None):
        self.default=default
        self.ImgLeft=Img1#cv2で扱える形にしたもの？
        self.ImgRight=Img2
        self.ImgLeft_name=Img2_name#元の形？
        self.ImgRight_name=Img2_name
        self.text_kari_backup = None
        pass

    def Img_reset(self):
        return #self.Img1,self.Img2

    def drowing_3Dview(self,text_kari):
        #↓defaultの黒い画面になってしまう
        #if self.text_kari_backup != text_kari:
        #    #cv2.imwrite(self.ImgLeft_name,self.default)
        #    #cv2.imwrite(self.ImgRight_name,self.default)
        #    self.ImgLeft=cv2.imread(self.default)
        #    self.ImgRight=cv2.imread(self.default)

        #    self.text_kari_backup = text_kari
            
        ##PIL型をopenCV型に変換 PIL型とは？
        #new_image = np.array(ImgLeft, dtype=np.uint8)
        #new_image = cv2.cvtColor(new_image, cv2.COLOR_RGB2BGR)
        cv2.putText(self.ImgLeft,text_kari,(200,40),drowing.font,1,(255,255,255),2)
        cv2.putText(self.ImgRight,text_kari,(200,40),drowing.font,1,(255,255,255),2)