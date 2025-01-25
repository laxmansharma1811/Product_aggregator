Product Aggregator
A project to compare product prices from various e-commerce platforms and provide historical analysis and product data. The system allows users to view prices, reviews, ratings, and detailed product information from multiple online retailers. It also features profile management functionalities like password reset and profile updates.

Features
Price Comparison: Aggregates product information from multiple e-commerce platforms such as Amazon, eBay, and others.
Historical Data Analysis: Offers insights into historical prices, helping users make informed decisions on the best time to buy products.
Profile Management:
User registration and login.
Password reset and change password functionalities.
Update and delete user profiles.
Product Detail View: Provides detailed product information, including price, description, and reviews.
Admin Panel: Allows admin users to upload and manage historical product data.
Installation
Follow the steps below to set up the project locally.

Prerequisites
Ensure you have the following installed:

Python 3.8+
Django 4.x+
PostgreSQL (or any other database of choice)
Git
Virtual environment tool (optional but recommended)
Clone the Repository
Clone the repository to your local machine using the command:

bash
Copy
Edit
git clone https://github.com/laxmansharma1811/Product_aggregator.git
Setup Virtual Environment (Optional but Recommended)
Create a virtual environment:

bash
Copy
Edit
python -m venv venv
Activate the virtual environment:

On Windows:
bash
Copy
Edit
venv\Scripts\activate
On Mac/Linux:
bash
Copy
Edit
source venv/bin/activate
Install Dependencies
Navigate to the project folder and install the required dependencies:

bash
Copy
Edit
cd Product_aggregator
pip install -r requirements.txt
Database Configuration
Configure your database settings in product_aggregator/settings.py. You can use SQLite (default) or set up PostgreSQL (recommended for production).

Run database migrations:

bash
Copy
Edit
python manage.py migrate
Create Superuser (Optional)
To access the Django admin panel, create a superuser by running the following command:

bash
Copy
Edit
python manage.py createsuperuser
Run the Development Server
Start the development server with the following command:

bash
Copy
Edit
python manage.py runserver
You can access the project in your browser at http://127.0.0.1:8000/.

File Structure
graphql
Copy
Edit
Product_aggregator/
├── aggregator_app/                   # Core application with all features
│   ├── migrations/                   # Database migrations
│   ├── management/                   # Commands for data import/export
│   ├── templates/                    # HTML templates for the app
│   └── models.py                     # Database models (User, Product, Historical Data)
├── product_aggregator/                # Project configuration and settings
│   ├── settings.py                   # Django settings
│   └── urls.py                       # URLs for the app
├── requirements.txt                  # Python dependencies
└── manage.py                         # Django project management commands
Usage
Price Comparison: Search for products from different e-commerce platforms and compare prices.
Historical Analysis: View the historical price trends of products to help make purchasing decisions.
User Profile Management: Create an account, reset your password, and update your profile information.
Admin Panel: Admins can manage the product data, including uploading historical data.
