import click

@click.group()
def cli():
    pass

@cli.command()
@click.option('--scrape-for', default=60, help='How long to scrape for, in minutes')
@click.option('--num-epochs', default=1000, help='Number of epochs to train the model for')
@click.option('--fresh', default=False, help='Whether to start from scratch with the model. \
                                              Doesn\'t delete entries.txt. Defaults to false.')
@click.option('--model-name', default='124M', help='Which GPT2 model to start with. Defaults to 124M')
def train_model(scrape_for, num_epochs, fresh, model_name):
    import scraper
    import asyncio

    if scrape_for >= 60:
        hours = scrape_for // 60
        remaining_minutes = scrape_for % 60
        print(f'Scraping for {hours} hours and {remaining_minutes} minutes...')
    else:
        print(f'Scraping for {scrape_for} minutes...')
    asyncio.run(scraper.get_all_definitions(scrape_for))

    print(f'\n\nDone scraping.')
    import train
    train.download_model(model_name)

    print(f'Done. Training...')
    train.write_pretty_dictionary()
    train.train_model(model_name, num_epochs=num_epochs, fresh=fresh)

@cli.command()
@click.option('--length', default=100, help='Number of samples to generate. Defaults to 1000')
def generate(length):
    import train

    print(f'Generating {length} samples... (this can take a while)')
    train.generate_output(length=length)

if __name__ == '__main__':
    cli()