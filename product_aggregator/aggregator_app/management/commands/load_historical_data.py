import random
import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from aggregator_app.models import Product, HistoricalData

class Command(BaseCommand):
    help = 'Generate random historical data for products'

    def handle(self, *args, **kwargs):
        # Get all products
        products = Product.objects.all()

        # Generate random historical data for each product
        for product in products:
            num_of_records = random.randint(5, 6)  # Generate 5 or 6 random records
            
            # Clean the product price (remove currency symbol, commas, and extra spaces)
            current_price_str = str(product.product_price).replace('रु', '').replace('Rs.', '').replace(',', '').strip()
            try:
                current_price = float(current_price_str)  # Convert cleaned price to float
            except ValueError:
                self.stdout.write(self.style.ERROR(f"Failed to convert price: {product.product_price}"))
                continue  # Skip this product if the price is invalid
            
            current_rating = product.rating

            for _ in range(num_of_records):
                # Generate a random price within ±5% of the current price (realistic range)
                price_variation = random.uniform(-0.05, 0.05)  # ±5%
                random_price = int(round(current_price * (1 + price_variation)))  # Round to nearest integer

                # Ensure that the price is still a reasonable value (e.g., no absurdly low prices)
                random_price = max(1000, random_price)  # Avoid very low prices like 1 or 20
                random_price = min(1000000, random_price)  # Avoid excessively high prices

                # Generate random rating within ±0.5 of the current rating, ensuring it's between 3.0 and 5.0
                rating_variation = random.uniform(-0.5, 0.5)  # ±0.5
                random_rating = round(current_rating + rating_variation, 1)
                random_rating = max(3.0, min(random_rating, 5.0))  # Ensure rating stays within [3.0, 5.0]

                # Generate a random date within the last 60 days
                random_date = timezone.now() - datetime.timedelta(days=random.randint(1, 60))

                # Create a new HistoricalData record
                HistoricalData.objects.create(
                    product=product,
                    price=random_price,
                    rating=random_rating,
                    date=random_date.date()
                )

        self.stdout.write(self.style.SUCCESS('Random historical data generated successfully.'))
