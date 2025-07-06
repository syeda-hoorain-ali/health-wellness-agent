import asyncio
import time
from uuid import uuid4
from colorama import Back, Fore, Style

from src.agent import HealthWellnessPlannerAgent
from src.context import UserSessionContext
import src.config

def welcome():
    print()
    print(Back.BLUE + Style.BRIGHT, '='*60 + ' ')
    print(' '*14, "Health & Wellness Planner Agent", ' '*15)
    print(' ' + '='*60, Style.RESET_ALL)
    print()

def exit():
    print()
    print(Back.BLUE + Style.BRIGHT, '='*60 + ' ')
    print(' '*19, "Thank you for visiting", ' '*19)
    print(' ' + '='*60, ' ', Style.RESET_ALL)
    print()
    
    
async def main():
    welcome()
    
    name = input("Please enter your name: ")    
    user = UserSessionContext(name=name, uid=str(uuid4()))
    agent = HealthWellnessPlannerAgent(user)
    
    while True:
        user_input = input(f"\n{Fore.MAGENTA + Style.BRIGHT}User:{Style.RESET_ALL} {Fore.BLACK + Style.DIM}(leave blank to exit) {Style.RESET_ALL}")
        
        if user_input.strip() == '':
            break
        
        result = agent.streaming(prompt=user_input)  

        print(Fore.MAGENTA + Style.BRIGHT + "Agent: " + Style.RESET_ALL, end='', flush=True)        
        async for chunk in result.chunks():
            print(chunk, end='', flush=True)
        
        print()
        time.sleep(1)
        
    
    # Print session summary with logfire logging
    agent.hooks.print_session_summary()
    exit()




if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
