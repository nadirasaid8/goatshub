import asyncio
from src.launcher import main
from src.deeplchain import banner,clear, log, mrh

if __name__ == "__main__":
    clear()
    banner()
    try:
        asyncio.run(main())
    except KeyboardInterrupt as e:
        log(f"{mrh}Stopping due to keyboard interrupt.")
        exit(0)
