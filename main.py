import asyncio
import handlers  # noqa
from loader import start_up

if __name__ == '__main__':
    try:
        asyncio.run(start_up())
    except KeyboardInterrupt:
        print('Хорош, бро')
