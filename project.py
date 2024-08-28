from mysql.connector import connection
import re
import datetime
import random
uname='root'
pword='password123'
hostname='127.0.0.1'
database_name='shopping_cart'
  
myconn=connection.MySQLConnection(host=hostname,user=uname,password=pword,database=database_name)
cur=myconn.cursor()

cur.execute('CREATE TABLE IF NOT EXISTS products (product_id INT NOT NULL AUTO_INCREMENT, product_name VARCHAR(255),product_price INT, product_warranty INT, product_description VARCHAR(1000), PRIMARY KEY (product_id))')
cur.execute('CREATE TABLE IF NOT EXISTS cart (cart_product_id INT NOT NULL AUTO_INCREMENT, cart_product_name VARCHAR(255), cart_product_price INT, cart_product_quantity INT, cart_product_warranty INT, PRIMARY KEY (cart_product_id))')
cur.execute('CREATE TABLE IF NOT EXISTS products_order (order_id VARCHAR(225) NOT NULL, order_product_name VARCHAR(255),order_product_quantity INT, order_product_price INT, order_product_total_cost FLOAT(10,2), order_date DATETIME)')
default_products = [
    ('Laptop',40000, 1, "Very good speed laptop for office purpose"),
    ('Headphones', 2000, 1, 'Music'),
    ('SamsungS22', 25000, 2, 'mobile phone'),
    ('Shirt', 1500, 1, 'make your style'),
    ('Pant', 2000, 1, 'jogger'),
    ('Apple', 25, 1, 'good for health'),
    ('Banana', 20, 2, 'strength'),
    ('Papaya', 15, 1, 'healty')
]
cur.executemany('Insert into products (product_name,product_price , product_warranty , product_description) values (%s,%s,%s,%s)',default_products)

myconn.commit()


class Product:
    @staticmethod
    def add_product(name, price, warranty, description):
        cur.execute('INSERT INTO products (product_name, product_price, product_warranty,  product_description) VALUES (%s, %s, %s, %s)', (name, price, warranty, description))
        myconn.commit()
        print(f"Product '{name}' added successfully.")

    @staticmethod
    def display_products():
        cur.execute('SELECT product_id,product_name,product_price,product_warranty,product_description FROM products')
        products = cur.fetchall()
        if products:
            print("\n-->> All available Produts to add to cart <<--\n")
            for product in products:
                print(f"Product ID: {product[0]}")
                print(f"Product Name:{product[1]}")
                print(f"Product Price:{product[2]}")
                print(f"Product Warranty:{product[3]}")
                print(f"Product Description:{product[4]}")
                print()
        else:
            print("No products available.")
class Cart:
    @staticmethod
    def add_to_cart(product_name, quantity):
        cur.execute('SELECT * FROM products WHERE product_name = %s', (product_name,))
        product = cur.fetchone()
        if product:
            cur.execute('INSERT INTO cart (cart_product_name, cart_product_price, cart_product_warranty, cart_product_quantity)  VALUES (%s, %s, %s, %s)', (product[1], product[2], product[3], quantity))
            myconn.commit()
            print(f"Added {quantity} of {product_name} to cart.")
        else:
            print(f"Product '{product_name}' not found.")
    @staticmethod
    def remove_from_cart(product_name):
        cur.execute('DELETE FROM cart WHERE cart_product_name = %s', (product_name,))
        myconn.commit()
        print(f"Removed {product_name} from cart.")

    @staticmethod
    def view_cart():
        cur.execute('SELECT * FROM cart')
        cart_items = cur.fetchall()
        if cart_items:
            print("\n-->> Display Produts From Cart <<--\n")
            print("Data exists:\n")
            for item in cart_items:
                print(f"Product Id: {item[0]}")
                print(f"Product Name:{item[1]}")
                print(f"Product Price: {item[2]}") 
                print(f"Product Quantity: {item[3]}") 
                print(f"Warranty: {item[4]} months")
                print()
        else:
            print("Cart is empty.")
    def update_quantity(product_name, quantity):
        cur.execute('UPDATE cart SET cart_product_quantity = %s WHERE cart_product_name = %s', (quantity, product_name))
        myconn.commit()
        print(f"Updated {product_name} quantity to {quantity}.")        
    def clear_cart():
        confirm = input("Are you sure you want to clear the cart? (yes/no): ")
        if confirm.lower() == 'yes':
            cur.execute('TRUNCATE TABLE cart')
            myconn.commit()
            print("Cart cleared.")
        else:
            print("Cart not cleared.")
class Order:
    @staticmethod
    def place_order(customer_name, phone_number, invoice_file_name):
        # Validate customer name and phone number
        if not re.match(r'^[a-zA-Z\s]+$', customer_name):
            print("Invalid customer name. It should only contain alphabets and spaces.")
            return
        if not re.match(r'^\+?(0|91)?[6-9]\d{9}$', phone_number):
            print("Invalid phone number. It should contain 10 digits.")
            return

        cur.execute('SELECT * FROM cart')
        cart_items = cur.fetchall()
        if not cart_items:
            print("Cart is empty. Cannot place order.")
            return
        order_id = f"{datetime.datetime.now().strftime(f'%Y%m%d%H%M%S')+str(random.randint(0, 9))}"
        order_date = datetime.datetime.now().strftime(f'%Y-%m-%d %H:%M:%S')
        
        with open(f"{invoice_file_name}.txt", "w") as invoice:
            invoice.write(f"Customer Name: {customer_name}\n")
            invoice.write(f"Phone Number: {phone_number}\n")
            invoice.write(f"Date: {order_date}\n")
            invoice.write(f"Order Id: {order_id}\n")
            invoice.write("\nProducts Ordered:\n")
            total_amount = 0
            for item in cart_items:
                price=int(item[2])
                quantity=int(item[3])
                line_total = price * quantity   
                total_amount += line_total
                invoice.write(f"{item[1]} x {item[3]}-W/S/ED-{item[4]} :$\t{line_total:.2f}\n")
                cur.execute('INSERT INTO products_order (order_id , order_product_name,  order_product_price, order_product_quantity, order_product_total_cost, order_date) VALUES (%s, %s, %s, %s, %s, %s)', (order_id, item[1], item[2], item[3], line_total, order_date))
            invoice.write("Note: Warranty various as per product. W-Warranty, S-Size,ED-Expiry Days")
            gst = total_amount * 0.1
            grand_total = total_amount + gst
            invoice.write("\n----------------------------------------------------------")
            invoice.write(f"\nSubtotal: ${total_amount:.2f}\n")
            invoice.write(f"GST (10%): ${gst:.2f}\n")
            invoice.write("----------------------------------------------------------\n")
            invoice.write(f"Total Amount: ${grand_total:.2f}\n")
            invoice.write("----------------------------------------------------------\n")
            invoice.write("Thank You Visit Again!")


        myconn.commit()

        cur.execute('TRUNCATE TABLE cart')
        myconn.commit()

        print(f"Order placed successfully. Invoice generated as {invoice_file_name+"Inovice"}.txt")


def main():
    while True:
        print("\n-->> Welcome <<--\n")
        print("\n--->> Start Online Shopping System <<---")
        print("1. Add Product into System")
        print("2. Display all available Products")
        print("3. Add Product to Cart")
        print("4. Remove Product from Cart")
        print("5. View Cart")
        print("6. Update item Quantity in Cart")
        print("7. Clear Cart")
        print("8. Place Order")
        print("9. Exit")

        choice = input("Enter your choice: ")
        if choice == '1':  #name, price, warranty, quantity, description
            print("\n-----------------------> Choose the Product Category <---------------------")
            print("1. Electronics")
            print("2. Clothing")
            print("3. Food")
            category=input("Enter product Category Choice:")
            if category=='1':
                name = input("Enter product name: ")
                price = int(input("Enter product price: "))
                warranty=int(input("Enter the warranty of the product:"))
                description=input("Enter the description:")
                Product.add_product(name, price, warranty,description)
            elif category=='2':
                name = input("Enter product name: ")
                price = int(input("Enter product price: "))
                warranty=int(input("Enter the warranty of the product:"))
                description=input("Enter the description:")
                Product.add_product(name, price, warranty, description)
            elif category=='3':
                name = input("Enter product name: ")
                price = int(input("Enter product price: "))
                warranty=int(input("Enter the warranty of the product:"))
                description=input("Enter the description:")
                Product.add_product(name, price, warranty,description)
            else:
                print("invalid option")
        elif choice == '2':
            Product.display_products()
        elif choice == '3':
            product_name = input("Enter product name to add to cart: ")
            quantity = int(input("Enter quantity: "))
            Cart.add_to_cart(product_name, quantity)
        elif choice == '4':
            product_name = input("Enter product name to remove from cart: ")
            Cart.remove_from_cart(product_name)
        elif choice == '5':
            Cart.view_cart()
        elif choice == '6':
            product_name = input("Enter product name to update quantity: ")
            quantity = int(input("Enter new quantity: "))
            Cart.update_quantity(product_name, quantity)
        elif choice == '7':
            Cart.clear_cart()
        elif choice == '8':
            customer_name = input("Enter customer name: ")
            phone_number = input("Enter phone number: ")
            invoice_file_name = input("Enter invoice file name: ")
            Order.place_order(customer_name, phone_number, invoice_file_name)
        elif choice == '9':
            print("Exiting the system. Thank you!")
            break
        else:
            print("Invalid choice. Please try again.")
if __name__ == "__main__":
    main()
cur.close()
myconn.close()