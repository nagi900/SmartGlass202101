from kivy.config import Config
Config.set('graphics', 'width', '640')#デフォルトでは800×600になっている
Config.set('graphics', 'height', '480')

from kivy.app import App
from kivy.uix.widget import Widget
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


class SmartGlassWidget(Widget):
    image_L = ObjectProperty(None)
    image_R = ObjectProperty(None)
    image_L_src = StringProperty("")
    image_R_src = StringProperty("")

    def __init__(self, **kwargs):
        super(SmartGlassWidget,self).__init__(**kwargs)
        #self.image_L_src = "./Discription/SmartGlass202101_sequence01.png"#"./Image_layer/ImgLeft_0.png"
        self.image_R_src = "./Image_layer/ImgRight_0.png"
        Clock.schedule_interval(self.update,0.01)
        pass

    def update(self,dt):
        print("更新")
        #self.image_L = self.image_L_src
        self.image_R_src = "./Image_layer/ImgRight_0.png"

    def StartbuttonClicked(self):
        handtracking.HandTracking().run()
    
class SmartGlassApp(App):
    def __init__(self,**kwargs):
        super(SmartGlassApp,self).__init__(**kwargs)
        self.title = "SmartGlass"

    def build(self):
        self.widget = SmartGlassWidget()
        return self.widget

    def set_image_src(self, src):
        self.widget.set_image_src(src)


def slides(app, a):
    dir_name = "./images"
    files = glob.glob(os.path.join(dir_name, "*.png"))

    while True:
        random.shuffle(files)
        for file_name in files:
            time.sleep(1)
            app.set_image_src(file_name)

if __name__ == "__main__":
    SmartGlassApp().run()