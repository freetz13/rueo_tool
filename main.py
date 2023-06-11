"""
This tool is used to lookup Esperanto words in rueo.ru
"""

import asyncio
import sys
from argparse import ArgumentParser

import aiohttp
from bs4 import BeautifulSoup

NOT_FOUND = 1


async def fetch(word: str) -> BeautifulSoup:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://old.rueo.ru/sercxo/{word}") as response:
            status = response.status
            content = await response.text()

    soup = BeautifulSoup(content, features="html.parser")
    result = soup.find("div", attrs={"class": "search_result"}).find("div")
    result.attrs.clear()  # Clean root element
    if kom := result.find("div", attrs={"class": "kom"}):
        kom.decompose()  # Remove comment
    return result


async def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("word", type=str)
    parser.add_argument(
        "--download", "-d", action="store_true", help="Download result as html"
    )
    args = parser.parse_args()

    result = await fetch(args.word)

    if (text := str(result)) == "<div>Подходящей словарной статьи не найдено.</div>":
        print("Слово не найдено")
        return NOT_FOUND

    print(result.text)

    if args.download:
        with open(f"{args.word}.html", "w") as file:
            file.write(text)


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
