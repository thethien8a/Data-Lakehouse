#!/usr/bin/env python3
"""
Mock Data Generator for E-commerce Lakehouse
Generates realistic sample data for orders, products, customers, and fx_rates
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import uuid
from faker import Faker
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EcommerceDataGenerator:
    def __init__(self, seed=42):
        """
        Initialize data generator with fixed seed for reproducibility
        """
        self.fake = Faker('en_US')
        random.seed(seed)
        np.random.seed(seed)

        # Product categories and their characteristics
        self.product_categories = {
            'Electronics': {'price_range': (10, 2000), 'margin': 0.3},
            'Clothing': {'price_range': (15, 500), 'margin': 0.4},
            'Books': {'price_range': (5, 100), 'margin': 0.5},
            'Home & Garden': {'price_range': (20, 800), 'margin': 0.35},
            'Sports': {'price_range': (25, 600), 'margin': 0.4},
            'Beauty': {'price_range': (8, 200), 'margin': 0.45}
        }

        # Countries and currencies
        self.countries_currencies = {
            'US': 'USD', 'UK': 'GBP', 'DE': 'EUR', 'FR': 'EUR',
            'IT': 'EUR', 'ES': 'EUR', 'NL': 'EUR', 'CA': 'CAD',
            'AU': 'AUD', 'JP': 'JPY', 'CN': 'CNY', 'IN': 'INR'
        }

        logger.info("🎲 Initialized E-commerce Data Generator")

    def generate_customers(self, n_customers=10000):
        """
        Generate customer data

        Args:
            n_customers (int): Number of customers to generate

        Returns:
            pd.DataFrame: Customer data
        """
        logger.info(f"👥 Generating {n_customers} customers...")

        customers = []
        countries = list(self.countries_currencies.keys())

        for i in range(n_customers):
            country = random.choice(countries)
            customers.append({
                'customer_id': f"CUST_{i+1:06d}",
                'customer_name': self.fake.name(),
                'email': self.fake.email(),
                'phone': self.fake.phone_number(),
                'address': self.fake.address().replace('\n', ', '),
                'city': self.fake.city(),
                'country': country,
                'currency': self.countries_currencies[country],
                'registration_date': self.fake.date_between(start_date='-2y', end_date='today'),
                'segment': random.choice(['Bronze', 'Silver', 'Gold', 'Platinum']),
                'total_orders': random.randint(0, 50),
                'total_spent': round(random.uniform(0, 10000), 2),
                'last_order_date': self.fake.date_between(start_date='-1y', end_date='today') if random.random() > 0.1 else None
            })

        df = pd.DataFrame(customers)
        logger.info(f"✅ Generated {len(df)} customers")
        return df

    def generate_products(self, n_products=5000):
        """
        Generate product catalog

        Args:
            n_products (int): Number of products to generate

        Returns:
            pd.DataFrame: Product data
        """
        logger.info(f"📦 Generating {n_products} products...")

        products = []
        categories = list(self.product_categories.keys())

        for i in range(n_products):
            category = random.choice(categories)
            base_price = random.uniform(*self.product_categories[category]['price_range'])
            margin = self.product_categories[category]['margin']

            products.append({
                'product_id': f"PROD_{i+1:06d}",
                'product_name': self._generate_product_name(category),
                'category': category,
                'subcategory': self._generate_subcategory(category),
                'brand': self.fake.company(),
                'description': self.fake.sentence(),
                'base_price': round(base_price, 2),
                'sale_price': round(base_price * (1 + random.uniform(-0.3, 0.1)), 2),  # Some discounts
                'cost_price': round(base_price * (1 - margin), 2),
                'currency': 'USD',  # Base currency
                'stock_quantity': random.randint(0, 1000),
                'min_stock_level': random.randint(10, 100),
                'supplier_id': f"SUP_{random.randint(1, 100):03d}",
                'is_active': random.random() > 0.05,  # 95% active
                'created_date': self.fake.date_between(start_date='-1y', end_date='today'),
                'last_updated': self.fake.date_between(start_date='-6M', end_date='today')
            })

        df = pd.DataFrame(products)
        logger.info(f"✅ Generated {len(df)} products")
        return df

    def _generate_product_name(self, category):
        """Generate realistic product names based on category"""
        templates = {
            'Electronics': [
                'Wireless {}', 'Bluetooth {}', 'Smart {}', 'Portable {}',
                'Gaming {}', 'Professional {}', '{} Pro', '{} Max'
            ],
            'Clothing': [
                'Classic {}', 'Premium {}', 'Casual {}', 'Designer {}',
                'Comfort {}', 'Athletic {}', '{} Collection', 'Vintage {}'
            ],
            'Books': [
                'The Art of {}', 'Mastering {}', 'Guide to {}', 'Essentials of {}',
                '{} Handbook', 'Advanced {}', '{} for Beginners', 'Complete {}'
            ],
            'Home & Garden': [
                'Modern {}', 'Rustic {}', 'Garden {}', 'Indoor {}',
                'Decorative {}', 'Functional {}', 'Luxury {}', 'Compact {}'
            ],
            'Sports': [
                'Professional {}', 'Training {}', 'Performance {}', 'Extreme {}',
                'Athletic {}', 'Competition {}', '{} Gear', 'Elite {}'
            ],
            'Beauty': [
                'Luxury {}', 'Natural {}', 'Professional {}', 'Organic {}',
                'Anti-Aging {}', 'Hydrating {}', 'Repairing {}', 'Nourishing {}'
            ]
        }

        items = {
            'Electronics': ['Headphones', 'Speaker', 'Mouse', 'Keyboard', 'Monitor', 'Laptop', 'Tablet', 'Phone'],
            'Clothing': ['T-Shirt', 'Jeans', 'Jacket', 'Dress', 'Shoes', 'Hat', 'Scarf', 'Gloves'],
            'Books': ['Programming', 'Cooking', 'Photography', 'Gardening', 'Business', 'History', 'Science', 'Art'],
            'Home & Garden': ['Lamp', 'Chair', 'Table', 'Plant', 'Decor', 'Storage', 'Lighting', 'Furniture'],
            'Sports': ['Shoes', 'Ball', 'Racket', 'Bike', 'Gloves', 'Helmet', 'Jersey', 'Equipment'],
            'Beauty': ['Cream', 'Serum', 'Mask', 'Oil', 'Lotion', 'Soap', 'Shampoo', 'Conditioner']
        }

        template = random.choice(templates[category])
        item = random.choice(items[category])
        return template.format(item)

    def _generate_subcategory(self, category):
        """Generate subcategories for products"""
        subcategories = {
            'Electronics': ['Audio', 'Computing', 'Gaming', 'Mobile', 'Wearables'],
            'Clothing': ['Tops', 'Bottoms', 'Outerwear', 'Footwear', 'Accessories'],
            'Books': ['Fiction', 'Non-Fiction', 'Educational', 'Reference', 'Biography'],
            'Home & Garden': ['Furniture', 'Decor', 'Kitchen', 'Garden', 'Lighting'],
            'Sports': ['Team Sports', 'Individual Sports', 'Fitness', 'Outdoor', 'Water Sports'],
            'Beauty': ['Skincare', 'Haircare', 'Makeup', 'Fragrance', 'Nails']
        }
        return random.choice(subcategories[category])

    def generate_fx_rates(self, start_date=None, days=365):
        """
        Generate foreign exchange rates

        Args:
            start_date (str): Start date in YYYY-MM-DD format
            days (int): Number of days to generate

        Returns:
            pd.DataFrame: FX rates data
        """
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

        logger.info(f"💱 Generating FX rates for {days} days...")

        start = datetime.strptime(start_date, '%Y-%m-%d')
        dates = [start + timedelta(days=i) for i in range(days)]

        fx_data = []

        # Base rates (approximate real-world rates)
        base_rates = {
            'GBP': 0.75, 'EUR': 0.85, 'CAD': 1.25, 'AUD': 1.35,
            'JPY': 110.0, 'CNY': 6.45, 'INR': 74.5
        }

        for date in dates:
            for currency, base_rate in base_rates.items():
                # Add some daily volatility (±5%)
                daily_rate = base_rate * (1 + random.uniform(-0.05, 0.05))

                fx_data.append({
                    'date': date.date(),
                    'currency': currency,
                    'rate_to_usd': round(daily_rate, 4),
                    'usd_to_currency': round(1 / daily_rate, 4)
                })

        df = pd.DataFrame(fx_data)
        logger.info(f"✅ Generated {len(df)} FX rate records")
        return df

    def generate_orders(self, customers_df, products_df, n_orders=50000, start_date=None):
        """
        Generate order data

        Args:
            customers_df (pd.DataFrame): Customer data
            products_df (pd.DataFrame): Product data
            n_orders (int): Number of orders to generate
            start_date (str): Start date for orders

        Returns:
            pd.DataFrame: Order data
        """
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')

        logger.info(f"🛒 Generating {n_orders} orders...")

        orders = []
        customer_ids = customers_df['customer_id'].tolist()
        product_ids = products_df['product_id'].tolist()

        start = datetime.strptime(start_date, '%Y-%m-%d')

        for i in range(n_orders):
            customer_id = random.choice(customer_ids)
            customer_info = customers_df[customers_df['customer_id'] == customer_id].iloc[0]

            # Generate order date (more recent orders have higher probability)
            days_back = int(random.betavariate(2, 5) * 365)  # Skew towards recent dates
            order_date = start + timedelta(days=days_back)

            # Generate order details
            num_items = random.randint(1, 10)
            order_items = []

            for _ in range(num_items):
                product_id = random.choice(product_ids)
                product_info = products_df[products_df['product_id'] == product_id].iloc[0]

                quantity = random.randint(1, 5)
                unit_price = product_info['sale_price']
                discount = round(random.uniform(0, 0.2), 2) if random.random() > 0.7 else 0

                order_items.append({
                    'product_id': product_id,
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'discount': discount,
                    'line_total': round((unit_price * quantity) * (1 - discount), 2)
                })

            order_total = sum(item['line_total'] for item in order_items)

            orders.append({
                'order_id': f"ORD_{i+1:08d}",
                'customer_id': customer_id,
                'order_date': order_date.date(),
                'order_status': random.choice(['Completed', 'Shipped', 'Processing', 'Cancelled']),
                'payment_method': random.choice(['Credit Card', 'PayPal', 'Bank Transfer', 'Cash on Delivery']),
                'currency': customer_info['currency'],
                'subtotal': order_total,
                'tax_amount': round(order_total * 0.08, 2),  # 8% tax
                'shipping_cost': round(random.uniform(0, 50), 2),
                'discount_amount': round(order_total * random.uniform(0, 0.15), 2),
                'total_amount': round(order_total * 1.08 + random.uniform(0, 50) - (order_total * random.uniform(0, 0.15)), 2),
                'items': order_items,
                'shipping_address': customer_info['address'],
                'billing_address': customer_info['address'],
                'created_at': order_date,
                'updated_at': order_date + timedelta(hours=random.randint(1, 24))
            })

        df = pd.DataFrame(orders)
        logger.info(f"✅ Generated {len(df)} orders")
        return df

    def generate_all_data(self, scale='small'):
        """
        Generate complete dataset for all tables

        Args:
            scale (str): 'small', 'medium', or 'large'

        Returns:
            dict: Dictionary containing all DataFrames
        """
        scales = {
            'small': {'customers': 1000, 'products': 500, 'orders': 5000},
            'medium': {'customers': 10000, 'products': 5000, 'orders': 50000},
            'large': {'customers': 50000, 'products': 25000, 'orders': 250000}
        }

        if scale not in scales:
            raise ValueError("Scale must be 'small', 'medium', or 'large'")

        config = scales[scale]
        logger.info(f"🚀 Generating {scale} scale dataset: {config}")

        # Generate base data
        customers_df = self.generate_customers(config['customers'])
        products_df = self.generate_products(config['products'])
        fx_rates_df = self.generate_fx_rates()

        # Generate orders (depends on customers and products)
        orders_df = self.generate_orders(customers_df, products_df, config['orders'])

        return {
            'customers': customers_df,
            'products': products_df,
            'orders': orders_df,
            'fx_rates': fx_rates_df
        }

    def save_to_parquet(self, data_dict, output_dir='data/mock'):
        """
        Save all generated data to Parquet files

        Args:
            data_dict (dict): Dictionary of DataFrames
            output_dir (str): Output directory
        """
        import os
        os.makedirs(output_dir, exist_ok=True)

        for table_name, df in data_dict.items():
            file_path = f"{output_dir}/{table_name}.parquet"
            df.to_parquet(file_path, index=False)
            logger.info(f"💾 Saved {table_name}: {len(df)} rows to {file_path}")


if __name__ == "__main__":
    # Example usage
    generator = EcommerceDataGenerator()

    # Generate small dataset for testing
    logger.info("🎬 Generating sample dataset...")
    data = generator.generate_all_data(scale='small')

    # Save to local files
    generator.save_to_parquet(data)

    # Display summary
    print("\n📊 Generated Dataset Summary:")
    for table_name, df in data.items():
        print(f"  • {table_name}: {len(df)} rows, {len(df.columns)} columns")
        print(f"    Columns: {', '.join(df.columns[:5])}{'...' if len(df.columns) > 5 else ''}")
