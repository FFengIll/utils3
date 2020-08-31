import time
import threading
from multiprocessing import Process, Queue


class Timer():
    CANCELED= 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setup(self,sec):
        def decorator2(func):
            def innner(*args,**kwargs):
                q = Queue()

                # We create a Process
                action_process = Process(target=func,args=(q,))
            
                # We start the process and we block for 5 seconds.
                action_process.start()
                action_process.join(timeout=sec)
            
                # We terminate the process.
                # FIXME: it is not safe enough to terminate.
                action_process.terminate()
                print('complete or timeout!')
                print(q.get())

            return innner

        def decorator(func):

            def sleep(sec):
                print('sleep')
                time.sleep(sec)
                raise KeyboardInterrupt

            def inner(*args,**kwargs):
                try:
                    t= threading.Thread(target= sleep,args= (sec, ) )
                    t.setDaemon(True)
                    t.start()

                    task = threading.Thread(target= func,args=args,kwargs=kwargs )
                    task.start()
                except KeyboardInterrupt as kie:
                    print('time out or user interrupt')
                    exit()

                    return 
                except Exception as e:
                    raise e
                
                return
            
            return inner

        return decorator2

    def cancel(self):
        self.status = Timer.CANCELED

    def start(self):
        pass

def test_timer():

    timer = Timer()

    @timer.setup(3)
    def run(q):
        print('will sleep 100')
        q.put(1)
        time.sleep(100)
        print('complete sleep 100')

    run()


if __name__ == "__main__":
    test_timer()