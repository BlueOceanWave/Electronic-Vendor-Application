CREATE TABLE Customer (
    customer_id varchar(20) PRIMARY KEY,
    customer_name varchar(20),
    customer_email varchar(30),
    customer_password varchar(20) CHARACTER SET latin1 COLLATE latin1_general_cs DEFAULT NULL,
    contract int DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE Address (
    address_id varchar(20),
    street varchar(20),
    city varchar(20),
    state varchar(20),
    country varchar(30),
    zipcode varchar(20),
    PRIMARY KEY (address_id)
);

CREATE TABLE Credit (
    credit_id varchar(20),
    balance numeric(12,2),
    PRIMARY KEY (credit_id)
);

CREATE TABLE Warehouse (
    warehouse_id varchar(20),
    address_id varchar(20),
    PRIMARY KEY (warehouse_id),
    FOREIGN KEY (address_id) REFERENCES address(address_id)
);


CREATE TABLE Products (
    pid varchar(20),
    pname varchar(40),
    price numeric(12,2),
    PRIMARY KEY (pid)
);

CREATE TABLE Temp_cart (
	customer_id varchar(20),
    pid varchar(20),
    qty int,
    PRIMARY KEY (customer_id, pid),
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id),
    FOREIGN KEY (pid) REFERENCES products(pid)
);

CREATE TABLE Categories (
    category_id varchar(20),
    category varchar(20),
    PRIMARY KEY (category_id)
);

CREATE TABLE Online_Orders (
    tracking_id varchar(20),
    address_id varchar(20),
    PRIMARY KEY (tracking_id),
    FOREIGN KEY (address_id) REFERENCES Address(address_id)
);

CREATE TABLE Cart (
    cart_id varchar(20),
    pid varchar(20),
    cart_quantity int DEFAULT 1,
    PRIMARY KEY (cart_id, pid),
    FOREIGN KEY (pid) REFERENCES Products(pid)
);

CREATE TABLE Store (
    store_id varchar(20),
    address_id varchar(20),
    PRIMARY KEY (store_id),
    FOREIGN KEY (address_id) REFERENCES Address(address_id)
);

CREATE TABLE Employee (
    employee_id varchar(20),
    employee_name varchar(20),
    employee_email varchar(30),
    employee_password varchar(20) CHARACTER SET latin1 COLLATE latin1_general_cs DEFAULT NULL,
    PRIMARY KEY (employee_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE Sales (
    sale_id varchar(20),
    total_price numeric(12,2),
    sale_time timestamp DEFAULT CURRENT_TIMESTAMP(),
    PRIMARY KEY (sale_id)
);

CREATE TABLE Reorder (
    reorder_id varchar(20),
    store_id varchar(20),
    pid varchar(20),
    warehouse_id varchar(20),
    reorder_quantity int,
    PRIMARY KEY (reorder_id),
    FOREIGN KEY (store_id) REFERENCES Store(store_id),
    FOREIGN KEY (pid) REFERENCES Products(pid),
    FOREIGN KEY (warehouse_id) REFERENCES warehouse(warehouse_id)
);

-- this is a relationship between Products and Store
CREATE TABLE Inventory (
    pid varchar(20),
    store_id varchar(20),
    inventory_quantity int,
    PRIMARY KEY (pid, store_id),
    FOREIGN KEY (pid) REFERENCES Products(pid),
    FOREIGN KEY (store_id) REFERENCES Store(store_id)
); 

-- relationship betwen Produts and Categories named Category
CREATE TABLE Category (
    pid varchar(20),
    category_id varchar(20),
    PRIMARY KEY (pid, category_id),
    FOREIGN KEY (pid) REFERENCES Products(pid),
    FOREIGN KEY (category_id) REFERENCES Categories(category_id)
);

-- relationship between Warehouse and Products named Carries
CREATE TABLE Carries (
    pid varchar(20),
    warehouse_id varchar(20),
    carries_quantity int,
    PRIMARY KEY (pid, warehouse_id),
    FOREIGN KEY (pid) REFERENCES Products(pid),
    FOREIGN KEY (warehouse_id) REFERENCES Warehouse(warehouse_id)
);

-- relationship between Employee and store_id named Works_For
CREATE TABLE Works_For (
    employee_id varchar(20),
    store_id varchar(20),
    PRIMARY KEY (employee_id, store_id),
    FOREIGN KEY (employee_id) REFERENCES Employee(employee_id),
    FOREIGN KEY (store_id) REFERENCES store(store_id)
);

-- relationship between Employee and Employee names Manages
CREATE TABLE Manages (
    employee_id1 varchar(20),
    employee_id2 varchar(20),
    PRIMARY KEY (employee_id1, employee_id2),
    FOREIGN KEY (employee_id1) REFERENCES Employee(employee_id),
    FOREIGN KEY (employee_id2) REFERENCES Employee(employee_id)
);

-- relationship between Customer and Credit named Has_Credit
CREATE TABLE Has_Credit (
    customer_id varchar(20),
    credit_id varchar(20),
    PRIMARY KEY (customer_id, credit_id),
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id),
    FOREIGN KEY (credit_id) REFERENCES Credit(credit_id)
);


-- relationship between Online_Orders and Cart
CREATE TABLE Online_Cart (
    tracking_id varchar(20),
    cart_id varchar(20),
    pid varchar(20),
    PRIMARY KEY (tracking_id, cart_id, pid),
    FOREIGN KEY (tracking_id) REFERENCES Online_Orders(tracking_id),
    FOREIGN KEY (cart_id, pid) REFERENCES Cart(cart_id, pid) ON DELETE CASCADE
);

-- relationship betwen Sales and Cart named Sales_Cart
CREATE TABLE Sales_Cart (
    sale_id varchar(20),
    cart_id varchar(20),
    pid varchar(20),
    PRIMARY KEY (sale_id, cart_id, pid),
    FOREIGN KEY (sale_id) REFERENCES Sales(sale_id),
    FOREIGN KEY (cart_id, pid) REFERENCES Cart(cart_id, pid) ON DELETE CASCADE
);

CREATE TABLE Customer_Address (
	customer_id varchar(20), 
    address_id varchar(20),
    PRIMARY KEY (customer_id, address_id),
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id),
    FOREIGN KEY (address_id) REFERENCES Address(address_id)
);

CREATE TABLE Order_History (
	customer_id varchar(20),
    tracking_id varchar(20),
    PRIMARY KEY (customer_id, tracking_id),
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id),
	FOREIGN KEY (tracking_id) REFERENCES online_orders(tracking_id)
);




-- Insert customers and employees
INSERT INTO customer values ("00001","Bob Marley", "customer1@gmail.com", "password",0);
INSERT INTO customer values ("00002","Harley Davidson", "customer2@gmail.com", "wordpass",0);
INSERT INTO customer values ("00003","Samantha Bolie", "customer3@gmail.com", "password1",0);
INSERT INTO employee values ("00001","Tim Smith", "employee1@gmail.com", "Password");
INSERT INTO employee values ("00003","Alice Newman", "employee3@gmail.com", "Password");
INSERT INTO employee values ("00002","John Maizen", "employee2@gmail.com", "Password");

-- Insert Products
INSERT INTO products VALUES ("P0001", "Lenovo Yoga 7i Laptop", 1100);
INSERT INTO products VALUES ("P0002", "Lenovo ThinkPad Laptop", 700);
INSERT INTO products VALUES ("P0003", "Logitech Computer Mouse", 20);
INSERT INTO products VALUES ("P0004", "6ft HDMI Cable", 20);
INSERT INTO products VALUES ("P0005", "6ft USB-C Cable", 20);
INSERT INTO Products VALUES ("P0006", "MacBook Air", 1100);
INSERT INTO Products VALUES ("P0007", "HP Keyboard", 250);
INSERT INTO Products VALUES ("P0008", "JBL Mini Speaker", 80);
INSERT INTO Products VALUES ("P0009", "Gaming Monitor", 300);
INSERT INTO Products VALUES ("P0010", "iPad", 1200);
INSERT INTO Products VALUES ("P0011", "Samsung Galaxy", 900);
INSERT INTO Products VALUES ("P0012", "Smart Fridge", 500);
INSERT INTO Products VALUES ("P0013", "Treadmill", 3000);
INSERT INTO Products VALUES ("P0014", "OLED TV", 5000);
INSERT INTO Products VALUES ("P0015", "Electonic Weight Scale", 75);

-- Temprorary cart 
INSERT INTO temp_cart VALUES ("00001", "P0001", 1);
INSERT INTO temp_cart VALUES ("00001", "P0003", 1);
INSERT INTO temp_cart VALUES ("00001", "P0004", 1);

-- Addresses
INSERT INTO address VALUES ("A0001", "Michigane Ave.", "Chicago", "IL", "USA", "60605");
INSERT INTO Address VALUES ("A0005", "Pratt Blvd", "San Diego", "CA", "USA", "12935");
INSERT INTO Address VALUES ("A0006", "Brown street", "Des Moines", "IA", "USA", "11111");
INSERT INTO address VALUES ("A0003", "6454 Frontier Rd", "Denver", "CO", "USA", "34856");
INSERT INTO address VALUES ("A0002", "650 Main St", "Downers Grove", "IL", "USA", "60548");
INSERT INTO address VALUES ("A0004", "789 Concord Ave", "Milwaukee", "MI", "USA", "74865");

-- Give customer address
INSERT INTO customer_address VALUES ("00001", "A0002");
INSERT INTO customer_address VALUES ("00001", "A0006");
INSERT INTO customer_address VALUES ("00002", "A0004");
INSERT INTO customer_address VALUES ("00003", "A0005");

-- Stores
INSERT INTO store VALUES ("S0001", "A0001");

-- Store Inventories
INSERT INTO inventory VALUES ("P0001", "S0001", 5);
INSERT INTO inventory VALUES ("P0002", "S0001", 10);
INSERT INTO inventory VALUES ("P0003", "S0001", 20);
INSERT INTO inventory VALUES ("P0004", "S0001", 15);
INSERT INTO inventory VALUES ("P0005", "S0001", 20);
INSERT INTO inventory VALUES ("P0006", "S0001", 20);
INSERT INTO inventory VALUES ("P0007", "S0001", 30);
INSERT INTO inventory VALUES ("P0008", "S0001", 17);
INSERT INTO inventory VALUES ("P0009", "S0001", 26);
INSERT INTO inventory VALUES ("P0010", "S0001", 9);
INSERT INTO inventory VALUES ("P0011", "S0001", 28);

-- Warehouses
INSERT INTO warehouse VALUES ('W0001', "A0003");
INSERT INTO warehouse VALUES ('W0002', "A0004");

-- Warehouse inventories
INSERT INTO carries VALUES ("P0001", "W0002", 50);
INSERT INTO carries VALUES ("P0002", "W0002", 70);
INSERT INTO carries VALUES ("P0003", "W0001", 120);
INSERT INTO carries VALUES ("P0003", "W0002", 60);
INSERT INTO carries VALUES ("P0004", "W0001", 70);
INSERT INTO carries VALUES ("P0005", "W0001", 30);
INSERT INTO carries VALUES ("P0006", "W0002", 40);
INSERT INTO carries VALUES ("P0006", "W0001", 90);
INSERT INTO carries VALUES ("P0007", "W0002", 15);
INSERT INTO carries VALUES ("P0008", "W0001", 16);
INSERT INTO carries VALUES ("P0008", "W0002", 38);
INSERT INTO carries VALUES ("P0010", "W0001", 104);
INSERT INTO carries VALUES ("P0011", "W0002", 21);
INSERT INTO carries VALUES ("P0011", "W0001", 126);
INSERT INTO carries VALUES ("P0012", "W0002", 70);
INSERT INTO carries VALUES ("P0012", "W0001", 150);
INSERT INTO carries VALUES ("P0013", "W0002", 60);
INSERT INTO carries VALUES ("P0014", "W0001", 160);

-- Employee store relationship
INSERT INTO works_for VALUES ("00001", "S0001");

-- Categories
INSERT INTO categories VALUES ("C0001", "Laptops");
INSERT INTO categories VALUES ("C0002", "Computer Accessories");
INSERT INTO categories VALUES ("C0003", "Consumer Electronics");
INSERT INTO categories VALUES ("C0004", "Gaming");
INSERT INTO categories VALUES ("C0005", "Wires and Cables");
INSERT INTO categories VALUES ("C0006", "Health and Fitness");
INSERT INTO categories VALUES ("C0007", "Home Electronics");

-- Give each product a category
INSERT INTO category VALUES ("P0001","C0001");
INSERT INTO category VALUES ("P0002","C0001");
INSERT INTO category VALUES ("P0003","C0002");
INSERT INTO category VALUES ("P0004","C0005");
INSERT INTO category VALUES ("P0005","C0005");
INSERT INTO category VALUES ("P0006","C0001");
INSERT INTO category VALUES ("P0007","C0002");
INSERT INTO category VALUES ("P0008","C0003");
INSERT INTO category VALUES ("P0009","C0004");
INSERT INTO category VALUES ("P0010","C0003");
INSERT INTO category VALUES ("P0011","C0003");
INSERT INTO category VALUES ("P0012","C0007");
INSERT INTO category VALUES ("P0013","C0006");
INSERT INTO category VALUES ("P0014","C0007");
INSERT INTO category VALUES ("P0015","C0006"); 

-- Credit accounts
INSERT INTO credit VALUES ("CR001", 1500);
INSERT INTO credit VALUES ("CR002", 700);
INSERT INTO credit VALUES ("CR003", 6500);

-- Assign credit to customers
INSERT INTO has_credit VALUES ("00001", "CR001");
INSERT INTO has_credit VALUES ("00002", "CR002");
INSERT INTO has_credit VALUES ("00003", "CR003");


-- Define managers
INSERT INTO manages VALUES ("00002","00001");
INSERT INTO manages VALUES ("00003","00002");

