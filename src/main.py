

import asyncio
import time
from uuid import uuid4
from colorama import Back, Fore, Style

from src.agent import HealthWellnessPlannerAgent
from src.context import UserSessionContext

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
    print(user)
    
    agent = HealthWellnessPlannerAgent(user)
    
    while True:
        user_input = input(f"\n{Fore.MAGENTA + Style.BRIGHT}User:{Style.RESET_ALL} {Fore.BLACK + Style.DIM}(leave blank to exit) {Style.RESET_ALL}")
        
        if user_input.strip() == '':
            break
        
        result = agent.streaming(prompt=user_input)  
        # result = "Lorem ipsum, dolor sit amet consectetur adipisicing elit. Voluptas deleniti earum, eaque reiciendis ut fugiat. Repudiandae, ipsum debitis? Cumque, quas nostrum impedit iste pariatur aperiam est veritatis explicabo nam tenetur? Atque labore debitis pariatur dicta vitae eos odio. Quasi ad beatae possimus tempore nesciunt perferendis quaerat officiis eveniet aliquam odio?"
        
        print(Fore.MAGENTA + Style.BRIGHT + "Agent: " + Style.RESET_ALL, end='', flush=True)
        # for chunk in result.split(' '):
        #     print(chunk, end=' ', flush=True)
        #     time.sleep(0.1)
        
        async for chunk in result.chunks():
            print(chunk, end='', flush=True)
        
        print()
        time.sleep(1)
        
    
    exit()




if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
