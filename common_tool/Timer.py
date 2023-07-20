import time


class Timer:  # @save
    """记录多次运行时间"""

    def __init__(self):
        self.tik = time.time()
        self.pre_tik = time.time()
        self.times = []
        self.start()

    def start(self):
        """启动计时器"""
        self.pre_tik = self.tik = time.time()

    def stop(self):
        """停止计时器并将时间记录在列表中"""
        self.times.append(time.time() - self.tik)
        self.start()
        return self.times[-1]

    def loop(self):
        """停止计时器并将时间记录在列表中"""
        tik_tag = time.time()
        loop_time = tik_tag - self.pre_tik
        self.pre_tik = tik_tag
        return loop_time

    def avg(self):
        """返回平均时间"""
        return sum(self.times) / len(self.times)

    def sum(self):
        """返回时间总和"""
        return sum(self.times)

    def cumsum(self):
        """返回累计时间"""
        return np.array(self.times).cumsum().tolist()
