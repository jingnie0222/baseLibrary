import time
import threading


class CountdownTimer(threading.Thread):
    def __init__(self, timer_start = 60):
        if timer_start <= 0:
            self.timer_start = 60
        else:
            self.timer_start = timer_start
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.thread_run = True

    def run(self):
        while self.thread_run and self.timer_start > 0:
            time.sleep(1)
            self.timer_start = self.timer_start - 1

    def stop(self):
        self.thread_run = False


def time_sleep(time_value = 0):
    if time_value < 0 or time_value > 1800:
        time_value = 0
    time.sleep(time_value)


# for test
if __name__ == "__main__":
    strat_time = int(time.time())
    timer = CountdownTimer(60)
    timer.start()
    print('timer start')
    while timer.isAlive():
        cost = int(time.time()) - strat_time
        print('cost:  ', cost)
        if cost > 30:
            timer.stop()
            print('timer break')
    print('timer end')