import time

#指定したジェスチャーをしてからどれだけ時間が経過したか返す
class Time_mesure:
    def __init__(self):
        super().__init__()
        self.time_count=0.0
        self.time_start=0.0
    
    def time_measu(self):
       #5秒以上経過していたらリセット
       if self.time_count > 5.0: 
           self.time_count = 0.0
           self.time_count = 0.0
           time_start = time.time()
       time_count = time.time() - time_start #time.time()で現在時刻

       return time_count
