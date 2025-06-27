from abc import ABC, abstractmethod

class Strategy(ABC):
    @abstractmethod
    def execute(self):
        raise NotImplementedError
    

class SendEmail(Strategy):
    def __init__(self, ):
        pass
    
    def execute(self):
        pass
    
    
    
class DecryptData(Strategy):
    def __init__(self, ):
        pass
    
    
    def execute(self):
        pass
    
    
    
class DeleteData(Strategy):
    def __init__(self):
        pass
    
    
    def execute(self):
        pass