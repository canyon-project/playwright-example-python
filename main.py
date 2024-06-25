import asyncio

from custom.base import custom_test

async def main():
    await custom_test.run_test()

if __name__ == "__main__":
    asyncio.run(main())
