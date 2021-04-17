from kivy.config import Config
Config.set('graphics', 'width', '640')#デフォルトでは800×600になっている
Config.set('graphics', 'height', '480')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.lang import Builder#これ何？
from kivy.uix.screenmanager import ScreenManager, Screen#, FadeTransition#画面遷移のやつ
from kivy.properties import StringProperty ,ObjectProperty
from kivy.core.text import LabelBase,DEFAULT_FONT#日本語を使えるようにする
from kivy.resources import resource_add_path #多分画像表示のパス取得用のやつ
from kivy.clock import Clock 
from kivy.graphics.texture import Texture
from kivy.graphics import Rectangle

import os
import glob
import random
import threading
import time

import handtracking

#resource_add_path("./fonts")#デフォルトのフォントを変更
#LabelBase.register(DEFAULT_FONT,"mplus-2c-regular.ttf") #日本語
#resource_add_path("./Image_layer")

class StartScreen(Screen):
    pass

class SmartGlassWidget(Screen):#WidgetとScreenの違いは？
    image_L_src = StringProperty("")#これは必ずクラス変数として書かないとself.image_L_srcが読み込めない なんで？
    image_R_src = StringProperty("")

    def __init__(self, **kwargs):
        super(SmartGlassWidget,self).__init__(**kwargs)
        self.image_L_src = "./Image_layer/ImgLeft_0.png"
        self.image_R_src = "./Image_layer/ImgRight_0.png"
        self.handtrackingApp=handtracking.Handtracking()

    def update(self,dt):
        self.handtrackingApp.run()
        self.ids.image_L.reload() #kvファイルでid:としていれば、pyファイルからは何もせずにself.idsから呼び出していい
        self.ids.image_R.reload()

    def StartbuttonClicked(self):
        Clock.schedule_interval(self.update,0.01)
        pass
    
class ScreenManagement(ScreenManager):
    pass

class MainApp(App):
    def __init__(self,**kwargs):
        super(MainApp,self).__init__(**kwargs)
        self.title = "SmartGlass"

    def build(self):
        return Builder.load_file("main.kv")

if __name__ == "__main__":
    MainApp().run()