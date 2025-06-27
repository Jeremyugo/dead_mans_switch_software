import os
import sys
import signal
from loguru import logger as log
import time
from getpass import getpass

from src.strategies import SendEmail
from src.deadman import DeadManSwitch

# test password to be used for testing rn, will be removed obviously, don't bother trying it lol
CORRECT_PASSWORD = 1234

strategies = [
    SendEmail(),
]

def clear_terminal() -> None:
    os.system('clear' if os.name == 'posix' else 'cls')
    
    return
    
    
def trigger_action() -> None:
    log.info('\n☠️ Dead man switch activated!')
    
    for strategy in strategies:
        strategy.execute()
    clear_terminal()
    
    try:
        os.remove(sys.argv[0])
    except Exception as e:
        print(f"Could not delete script: {e}")
    
    os.kill(os.getpid(), signal.SIGKILL)
    
    return 
    

def main(timeout: int) -> None:
    dms = DeadManSwitch(timeout=timeout, on_trigger=trigger_action)
    try:
        while True:
            start_time = time.time()
            log.info(f'You have {timeout} seconds to enter a password to reset the ☠️ dead man switch')
            
            while time.time() - start_time < dms.timeout:
                try:
                    _password = getpass(prompt='Password: ')
                    break
                except Exception:
                    continue
                
            if _password == CORRECT_PASSWORD:
                dms.reset()
                log.success('Dead man switch reset')
            else:
                log.error('Incorrect password...')
                break
    
    except KeyboardInterrupt:
        log.warning('Exiting...')
        dms.cancel()  
        
    return
    

if __name__ == '__main__':
    main(timeout=5)