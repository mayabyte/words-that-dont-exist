import click
import asyncio
import scraper

@click.command()
@click.option('--scrape-for', default=60, help='How long to scrape for, in minutes')
def cli(scrape_for):
    asyncio.run(scraper.get_all_definitions(scrape_for))
    import train

if __name__ == '__main__':
    cli()