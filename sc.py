import random
import time
import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from Tfapp.models import Product

class Command(BaseCommand):
    help = 'Scrape data and update the database with the results'

    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=60,
            help='Interval in seconds between scrapes (default: 60 seconds)',
        )

    def handle(self, *args, **kwargs):
        interval = kwargs['interval']

        while True:
            self.scrape_and_update()
            time.sleep(interval)

    def scrape_and_update(self):
        url = "https://www.temu.com"

        # Introduce random delay between requests (3 to 7 seconds)
        delay = random.uniform(3, 7)
        time.sleep(delay)

        # Add User-Agent randomization
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",
            # Add more User-Agent strings as needed
        ]
        headers = {
            "User-Agent": random.choice(user_agents)
        }

        # Fetch the HTML content
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")

        # Extract product information
        category = soup.find("meta", {"name": "keywords"})["content"]
        product_name = soup.find("meta", {"name": "title"})["content"]
        amount = soup.find("meta", {"property": "product:price:amount"})["content"]
        description = soup.find("meta", {"name": "description"})["content"]
        link = url

        # Check if the product with the same URL already exists in the database
        try:
            product = Product.objects.get(link=link)
            # If the product exists, update its information
            product.category = category
            product.product_name = product_name
            product.amount = amount
            product.description = description
            product.save()
            self.stdout.write(self.style.SUCCESS('Product updated successfully.'))
        except Product.DoesNotExist:
            # If the product doesn't exist, create a new entry
            product = Product(
                category=category,
                product_name=product_name,
                amount=amount,
                description=description,
                link=link
            )
            product.save()
            self.stdout.write(self.style.SUCCESS('Product created successfully.'))
