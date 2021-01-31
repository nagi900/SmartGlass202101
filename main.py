from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import StringProperty 
from kivy.core.text import LabelBase,DEFAULT_FONT#日本語を使えるようにする
from kivy.resources import resource_add_path #多分画像表示のパス取得用のやつ
from kivy.clock import Clock 
from kivy.graphics.texture import Texture

import cv2

from handtracking import HandTracking

#resource_add_path("./fonts")#デフォルトのフォントを変更
#LabelBase.register(DEFAULT_FONT,"mplus-2c-regular.ttf") #日本語


class SmartGlassWidget(Widget,HandTracking):
    left_window=StringProperty("")

    def __init__(self, **kwargs):
        super(SmartGlassWidget,self).__init__(**kwargs)

    def StartbuttonClicked(self):
        HandTracking.run()

    def Update(self):
        pass#self.ImgLeft = HandTracking.ImgLeft
    
class SmartGlassApp(App):
    def __init__(self,**kwargs):
        super(SmartGlassApp,self).__init__(**kwargs)
        self.title = "SmartGlass"
    def build(self):
        self.main_ImgLeft=cv2.imread("ImgLeft.png")
        texture = Texture.create()
        texture.blit_buffer(self.main_ImgLeft.tostring())
        return SmartGlassWidget()

if __name__ == "__main__":
    SmartGlassApp().run()