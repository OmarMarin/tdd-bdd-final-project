# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db, DataValidationError
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    #
    # ADD YOUR TEST CASES HERE
    #
    def test_read_a_product(self):
        """It should read a product"""
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        found_product = Product.find(product.id)
        self.assertEqual(found_product.id, product.id)
        self.assertEqual(found_product.name, product.name)
        self.assertEqual(found_product.description, product.description)
        self.assertEqual(found_product.price, product.price)

    def test_update_a_product(self):
        """It should update the product"""
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        product.description = "Mustang"
        original_id = product.id
        product.update()
        self.assertEqual(original_id, product.id)
        self.assertEqual(product.description, "Mustang")
        products = Product.all()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].id, original_id)
        self.assertEqual(products[0].description, "Mustang")

    def test_delete_a_product(self):
        """It should delete a product from db"""
        product = ProductFactory()
        product.id = None
        product.create()
        products = Product.all()
        self.assertEqual(len(products), 1)
        product.delete()
        products = Product.all()
        self.assertEqual(len(products), 0)

    def test_list_all_products(self):
        """It should list all products from database"""
        products = Product.all()
        self.assertEqual(products, [])
        for _ in range(3):
            product = ProductFactory()
            product.id = None
            product.create()
        products = Product.all()
        self.assertEqual(len(products), 3)

    def test_find_by_name(self):
        """It should find product from db by name"""
        for _ in range(3):
            product = ProductFactory()
            product.id = None
            product.create()
        name = Product.all()[0].name
        count = len([product for product in Product.all() if product.name == name])
        found = Product.find_by_name(name)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.name, name)

    def test_find_by_availability(self):
        """It should find product by availability"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.id = None
            product.create()
        avail = products[0].available
        count = len([product for product in products if product.available == avail])
        found = Product.find_by_availability(avail)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.available, avail)

    def test_find_by_category(self):
        """It should filter by category"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.id = None
            product.create()
        category = products[0].category
        count = len([product for product in products if product.category == category])
        found = Product.find_by_category(category)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.category, category)

    def test_find_by_price(self):
        """It should filter by price"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.id = None
            product.create()
        price = products[0].price
        count = len([product for product in products if product.price == price])
        found = Product.find_by_price(str(price))
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.price, price)

    def test_failed_update(self):
        """It should raise error while updating"""
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        product.description = "Bronco"
        product.id = None
        self.assertRaises(DataValidationError, product.update)

    def test_from_dictionary(self):
        """Testing creating product from dictionary"""
        data = {
            "id": None,
            "name": "Ranger",
            "price": "298765.56",
            "description": "Truck for heavy work",
            "available": True,
            "category": "Truck"
        }

        product = Product()
        product.deserialize(data)
        product.create()
        found = Product.find_by_name("Ranger")
        for product in found:
            self.assertIsNotNone(product.id)
            self.assertEqual(product.name, data["name"])
            self.assertEqual(product.description, data["description"])

    def test_from_dictionary_errors(self):
        """Must raise error with invalid input"""
        data = {
            "name": "Maverick",
            "description": "Truck to move in difficult roads",
            "price": 10000.99,
            "available": 1, # Here the invalid input
            "category": "Ban"
        }
        product = Product()
        self.assertRaises(DataValidationError, product.deserialize, data)
        data1 = {
            "name": "Maverick",
            "description": "Truck to move in difficult roads",
            "price": 10000.99,
            "available": True,
            "category": "Ban",
            "ids": False # Here the attribute error
        }
        product = Product()
        self.assertRaises(DataValidationError, product.deserialize, data1)
        data2 = {
            "name": "Maverick",
            "description": "Truck to move in difficult roads",
            "price": 10000.99,
            "available": True,
            "category": None # Here is the type error
        }
        product = Product()
        self.assertRaises(DataValidationError, product.deserialize, data2)
