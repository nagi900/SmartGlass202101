import time

#指定したジェスチャーをしてからどれだけ時間が経過したか返す
class timeMesure:
    def __init__(self):
        super().__init__()
        self.target_name=str
        self.time_infos={None:{}} #{target_name:{startTime: ,rapTime: }} 
    
    #handSignTextの読み取り誤差を考慮して、違うhandsignになったあと5秒以内に同じhandsignをした場合は、タイマーをリセットせずに計測した値を返す
    def targetCount(self,target_name):
        #記録していないならセットして0を返す
        if not (target_name in self.time_infos):
            self.target_name = target_name
            self.time_infos={self.target_name:{}}
            self.time_infos[self.target_name]["startTime"] = time.time()
            return 0.0

        self.target_name = target_name
        self.time_infos[self.target_name]["rapTime"] = time.time() - self.time_infos[self.target_name]["startTime"] #time.time()で現在時刻
        #5秒以上経過していたらリセット
        if self.time_infos[self.target_name]["rapTime"] > 5:
            self.time_infos[self.target_name] = {}
            self.time_infos[self.target_name]["startTime"] = time.time()
            self.time_infos[self.target_name]["rapTime"] = 0.0

        return self.time_infos[self.target_name]["rapTime"]
