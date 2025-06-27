import threading
from typing import Callable


class DeadManSwitch:
    def __init__(self, timeout: int, on_trigger: Callable):
        self.timeout = timeout
        self.on_trigger = on_trigger
        self.timer = None
        self.reset()
        
        return
    
        
    def reset(self) -> None:
        if self.timer:
            self.timer.cancel()
        self.timer = threading.Timer(interval=self.timeout, function=self.on_trigger)
        self.timer.start()
        
        return
    
    
    def cancel(self) -> None:
        if self.timer:
            self.timer.cancel()
            
        return 