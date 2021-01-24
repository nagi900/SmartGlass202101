import time

#指定したジェスチャーをしてからどれだけ時間が経過したか返す
class Time_mesure:
    def __init__(self):
        super().__init__()
        self.target_name="a"
        self.time_infos={None:{}} #{target_name:(start,count)} 
        #↑　~infos={}だけだとキーエラーになる 多分 duct1[key1][key2]=varrue てやるとkey1は作成されないんじゃないかな

    def time_target_set(self,target_name):
        print("time_target_setが呼び出されました")
        self.target_name = target_name
        self.time_infos={self.target_name:{}}
        self.time_infos[self.target_name]["0"] = time.time()
    
    def time_measu(self,target_name):
        print("time_measuが呼び出されました\nスタート時刻から現在時刻を引いた値を返します。")
        self.target_name = target_name
        self.time_infos[self.target_name]["1"] = time.time() - self.time_infos[self.target_name]["0"] #time.time()で現在時刻
        #5秒以上経過していたらリセット
        if self.time_infos[self.target_name]["1"] > 5.0:
            print("5秒経過したのでリセット")
            self.time_infos[self.target_name] = {}
            self.time_infos[self.target_name]["0"] = time.time()
            self.time_infos[self.target_name]["1"] = 0.0

        return self.time_infos[self.target_name]["1"]
