import time
import threading

GlobalTimer = None

def GetTimer():
    return GlobalTimer

def SetTimer(timer):
    global GlobalTimer
    GlobalTimer = timer


class Timer(object):
    def __init__(self):
        self.Tasks = []
        self.Mutex = threading.Lock()
        self.Started = False

    def AddTaskDelta(self, delta, task):
        timestamp = time.time() + delta
        self.AddTaskTimestamp(timestamp, task)

    def AddTaskTimestamp(self, ts, task):
        self.Mutex.acquire()
        try:
            self.Tasks.append([ts, task])
        finally:
            self.Mutex.release()

    def RunTasks(self):
        self.Mutex.acquire()
        try:
            now = time.time()
            tasks_to_do = [task for ts, task in self.Tasks if ts < now]
            self.Tasks = [[ts, task] for ts, task in self.Tasks if ts >= now]

            for task in tasks_to_do:
                task()
        finally:
            self.Mutex.release()

    def Start(self):
        self.Started = True
        timer = self
        def loop():
            while timer.Started:
                timer.RunTasks()
                time.sleep(1)

        self.Thread = threading.Thread(target = loop)
        self.Thread.start()

    def Stop(self):
        self.Started = False
        self.Thread.join(3)