import asyncio

from src.consumer import run_consumer


def main() -> None:
    asyncio.run(run_consumer())


if __name__ == "__main__":
    main()
