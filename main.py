import sys
import asyncio

from src.core import main
from src.deeplchain import _banner,_clear, log, mrh

if __name__ == "__main__":
    _clear()
    _banner()
    try:
        asyncio.run(main())
    except KeyboardInterrupt as e:
        log(f"{mrh}Stopping due to keyboard interrupt.")
        sys.exit()
