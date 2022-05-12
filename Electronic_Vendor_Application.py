import tkinter as tk
from tkinter import ttk
import mysql.connector
from tkinter.messagebox import askyesno, askquestion

# Fill in databse connection information here
db = mysql.connector.connect(host="",
                             user="",
                             password="",
                             db="")
cursor = db.cursor()

# Various Queries
getCustomer = "SELECT customer_id, customer_name FROM customer WHERE customer_email=%s AND customer_password=%s"
getEmployee = "SELECT employee_id, employee_name FROM employee WHERE employee_email=%s AND employee_password=%s"
getCustomerBalance = "SELECT balance FROM customer NATURAL INNER JOIN credit WHERE customer_id=%s"
getTempCart = "SELECT * FROM temp_cart NATURAL INNER JOIN products WHERE temp_cart.customer_id = %s"
removeTempCartItem = "DELETE FROM temp_cart WHERE temp_cart.customer_id=%s AND temp_cart.pid=%s"
getCustomerProductsBase = "SELECT pid, pname, price, category, inventory_quantity, city, state " \
                          "FROM products NATURAL INNER JOIN category NATURAL INNER JOIN Categories NATURAL LEFT OUTER JOIN Inventory NATURAL LEFT OUTER JOIN store NATURAL LEFT OUTER JOIN address"
addItemToCart = "INSERT INTO temp_cart VALUES (%s, %s, %s)"
getCustomerOrderHistory = "SELECT * " \
                          "FROM order_history NATURAL INNER JOIN online_orders NATURAL INNER JOIN online_cart NATURAL INNER JOIN cart NATURAL INNER JOIN sales_cart NATURAL INNER JOIN sales " \
                          "WHERE customer_id = %s"
getEmployeeProductBase = "SELECT category_id, pid, store_id, store.address_id as store_address_id, inventory_quantity, pname, price, carries.warehouse_id, carries_quantity, category, w.address_id as warehouse_address_id " \
                         "FROM store NATURAL INNER JOIN inventory NATURAL INNER JOIN products NATURAL INNER JOIN carries NATURAL INNER JOIN category NATURAL INNER JOIN categories inner join warehouse w on (w.warehouse_id = carries.warehouse_id) " \
                         "WHERE store.store_id = %s"
getStoreReorders = "SELECT * FROM reorders WHERE store_id = %s"
getAllManagers = "WITH RECURSIVE rec_manager (employee_id1, employee_id2) AS ( " \
                 "SELECT m.employee_id1, m.employee_id2 " \
                 "FROM manages m " \
                 "UNION ALL " \
                 "SELECT rec_manager.employee_id1, m2.employee_id2 " \
                 "FROM rec_manager, manages m2 " \
                 "WHERE rec_manager.employee_id2 = m2.employee_id1) " \
                 "SELECT DISTINCT employee_name " \
                 "FROM rec_manager INNER JOIN employee ON rec_manager.employee_id1 = employee.employee_id " \
                 "WHERE employee_id2 = %s"


# Root class
class Application(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self._frame = None
        self.switch_frame(Login)

    def switch_frame(self, frame_class, info=None):
        """Destroys current frame and replaces it with a new one."""
        new_frame = frame_class(self, info)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack()


# Creates a double-scrollbar frame template
class ScrollableFrame(tk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        hscrollbar = ttk.Scrollbar(self, orient=tk.HORIZONTAL)
        vscrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        sizegrip = ttk.Sizegrip(self)
        canvas = tk.Canvas(self, bd=0, highlightthickness=0, yscrollcommand=vscrollbar.set,
                           xscrollcommand=hscrollbar.set)
        vscrollbar.config(command=canvas.yview)
        hscrollbar.config(command=canvas.xview)

        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        hscrollbar.pack(fill=tk.X, side=tk.BOTTOM, expand=tk.FALSE)
        vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)
        sizegrip.pack(in_=hscrollbar, side=tk.BOTTOM, anchor="se")
        canvas.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=tk.TRUE)

        canvas.create_window(0, 0, window=self.scrollable_frame, anchor="nw")
        canvas.config(scrollregion=canvas.bbox("all"))
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)


# Login Page
class Login(tk.Frame):
    def __init__(self, master, info=None):
        self.person = tk.StringVar()
        tk.Frame.__init__(self, master)
        tk.Label(self, text="User Login Page").grid(row=1, column=1, columnspan=2)

        # Customer and Employee buttons
        customer = tk.Radiobutton(self, text="Customer", variable=self.person, value="customer")
        employee = tk.Radiobutton(self, text="Employee", variable=self.person, value="employee")
        employee.deselect()
        customer.select()
        employee.grid(row=2, column=1)
        customer.grid(row=2, column=2)

        # Email and Password input
        tk.Label(self, text="Email: ").grid(row=3, column=1)
        tk.Label(self, text="Password: ").grid(row=4, column=1)
        self.email = tk.Entry(self, width=35)
        self.password = tk.Entry(self, width=35)
        self.email.grid(row=3, column=2, padx=10)
        self.password.grid(row=4, column=2, padx=10)

        # Login button
        tk.Button(self, text="Login",
                  command=lambda: self.login(master, self.person)).grid(row=7, column=1, columnspan=2)

    def login(self, master, var):
        ''' Verifies login information with databse'''

        self.loginMode = var.get()
        email = self.email.get()
        password = self.password.get()

        # Execute different queries depending on option selected
        if self.loginMode == "customer":
            cursor.execute(getCustomer, (email, password))
            result = cursor.fetchall()
            nextWindow = CustomerHome

        else:
            cursor.execute(getEmployee, (email, password))
            result = cursor.fetchall()
            nextWindow = EmployeeHome

        # Handle errors and pass relevant information to the next page
        if len(result) == 0:
            tk.Label(self, text="Invalid Login", fg="red").grid(row=6, column=1, columnspan=2)
        else:
            if self.loginMode == "customer":
                info = {"customer_id": result[0][0],
                        "name": result[0][1]}
            else:
                info = {"employee_id": result[0][0],
                        "name": result[0][1]}

            master.switch_frame(nextWindow, info)


# All relevant Employee Pages
class EmployeeHome(tk.Frame):
    def __init__(self, master, info=None):
        tk.Frame.__init__(self, master)
        info['store_id'] = self.getEmployeeStore(info)

        # Display labels
        tk.Label(self, text=f"Hello {info['name']}").grid(row=1, column=1, columnspan=2)
        tk.Label(self, text=f"Manager(s): ").grid(row=2, column=1, padx=4, pady=4, )

        # Display all managers in a drop-down list
        allManagers = self.getManagers(info)
        managers = [i[0] for i in allManagers]
        if len(managers):
            print(managers)
            clicked_item = tk.StringVar()
            clicked_item.set(managers[0])
            drop = tk.OptionMenu(self, clicked_item, *managers)
            drop.grid(row=2, column=2)
        else:
            tk.Label(self, text="None").grid(row=2, column=2)

        # Menu option buttons
        tk.Button(self, text="Products", width=8, height=2,
                  command=lambda: master.switch_frame(EmployeeProducts, info)).grid(row=3, column=1, columnspan=1,
                                                                                    padx=3, pady=3)
        tk.Button(self, text="Pending\nReorders", width=8, height=2,
                  command=lambda: master.switch_frame(EmployeeReorders, info)).grid(row=3, column=2, columnspan=1,
                                                                                    padx=3, pady=3)
        tk.Button(self, text="Sales", width=8, height=2,
                  command=lambda: master.switch_frame(EmployeeSales, info)).grid(row=4, column=1, columnspan=2, padx=3,
                                                                                 pady=3)
        tk.Button(self, text="Logout", fg='red',
                  command=lambda: master.switch_frame(Login)).grid(row=5, column=1, columnspan=2, pady=5)

    def getEmployeeStore(self, info):
        """Gets the store the employee works for"""

        cursor.execute("SELECT store_id FROM employee NATURAL INNER JOIN works_for WHERE employee_id=%s",
                       (info['employee_id'],))
        try:
            result = cursor.fetchall()[0][0]
        except:
            result = None

        return result

    def getManagers(self, info):
        """ Gets the employee's managers"""
        cursor.execute(getAllManagers, (info['employee_id'],))
        return cursor.fetchall()

class EmployeeProducts(tk.Frame):
    def __init__(self, master, info=None):
        tk.Frame.__init__(self, master)
        tk.Label(self, text="Products").grid(row=1, column=1, columnspan=2)
        tk.Button(self, text="Back", fg='blue',
                  command=lambda: master.switch_frame(EmployeeHome, info)).grid(row=9, column=1, columnspan=2, pady=5)

        # Initialize warning variables
        self.success = None
        self.warning1 = None
        self.warning2 = None

        # Set sorting variables
        info.setdefault('sortName', 0)
        info.setdefault('sortCategory', 0)
        info.setdefault('sortPrice', 0)
        self.sortCategory = tk.IntVar(value=info['sortCategory'])
        self.sortName = tk.IntVar(value=info['sortName'])
        self.sortPrice = tk.IntVar(value=info['sortPrice'])

        # Display all categories available for filtering in a drop-down menu
        tk.Label(self, text='Filter By:').grid(row=4, column=1)
        info.setdefault('filterCategory', 'All Categories')
        cursor.execute("SELECT category FROM categories")
        db_categories = [i[0] for i in cursor.fetchall()]
        db_categories.insert(0, "All Categories")
        self.clicked_category = tk.StringVar()
        self.clicked_category.set(info['filterCategory'])
        drop = tk.OptionMenu(self, self.clicked_category, *db_categories)
        drop.grid(row=5, column=1)
        tk.Button(self, text='Apply Filter', command=lambda: self.applyFilter(master, info)).grid(row=6, column=1)

        products = ScrollableFrame(self, width=500)
        productList = self.filterList(master, info)

        # Apply sort depending on options selected
        info['sortOn'] = []
        if self.sortCategory.get():
            info['sortOn'].append("x[3]")
        if self.sortName.get():
            info['sortOn'].append("x[1]")
        if self.sortPrice.get():
            info['sortOn'].append("x[2]")
        if len(info['sortOn']): eval(f'productList.sort(key=lambda x: ({",".join(info["sortOn"])}))')

        # List products and relevant information
        self.entries = []
        for i in range(len(productList)):
            product = productList[i]
            f = tk.Frame(products.scrollable_frame)

            # Store relevant information for next page
            newInfo = dict(info)
            newInfo['pid'] = product[1]
            newInfo['pname'] = product[5]
            newInfo['store_id'] = product[2]
            newInfo['warehouse_id'] = product[7]
            newInfo['carries_quantity'] = product[8]
            newInfo['entry_index'] = i

            # Display information
            tk.Label(f, text=product[9], padx=10, width=15).pack(side="left")
            tk.Label(f, text=product[5], padx=20, width=20).pack(side="left")
            tk.Label(f, text=f"${product[6]}", padx=10, width=7).pack(side="left")
            tk.Label(f, text=f'Store stock: {product[4]}', padx=10, width=16).pack(side="left")
            tk.Label(f, text=f'Warehouse ID: {product[7]}', padx=20, width=15).pack(side="left")
            tk.Label(f, text=f'Warehouse stock: {product[8]}', padx=10, width=17).pack(side="left")

            # Reorder button
            self.entries.append(tk.Entry(f, width=3))
            self.entries[-1].pack(side="left")
            tk.Button(f, text="Place Reorder", padx=10, width=10,
                      command=lambda i=newInfo: self.placeReorder(master, i)).pack(side="left")
            f.pack()
        products.grid(row=2, column=1, columnspan=2)
        print(self.getEmployeeProducts(master, info))

        # Sorting buttons
        tk.Checkbutton(self, text="Category", variable=self.sortCategory, onvalue=1, offvalue=0,
                       command=lambda: master.switch_frame(EmployeeProducts, self.updateItem(info, 'sortCategory',
                                                                                             not info[
                                                                                                 'sortCategory']))).grid(
            row=5, column=2)
        tk.Checkbutton(self, text="Name", variable=self.sortName, onvalue=1, offvalue=0,
                       command=lambda: master.switch_frame(EmployeeProducts, self.updateItem(info, 'sortName', not info[
                           'sortName']))).grid(row=6, column=2)
        tk.Checkbutton(self, text="Price", variable=self.sortPrice, onvalue=1, offvalue=0,
                       command=lambda: master.switch_frame(EmployeeProducts, self.updateItem(info, 'sortPrice',
                                                                                             not info[
                                                                                                 'sortPrice']))).grid(
            row=7, column=2)
        tk.Label(self, text="Sort By: ").grid(row=4, column=2)

    def updateItem(self, d, key, value):
        """Updates a dictionary item inline"""

        x = dict(d)
        x[key] = value
        return x

    def applyFilter(self, master, info):
        """Refreshes page to apply filter"""

        info['filterCategory'] = self.clicked_category.get()
        master.switch_frame(EmployeeProducts, info)

    def filterList(self, master, info):
        """Filter product list depending on category selected"""

        if info['filterCategory'] != "All Categories":
            cursor.execute(f"SELECT * FROM ({getEmployeeProductBase}) a WHERE a.category=%s",
                           (info['store_id'], info['filterCategory']))
            return cursor.fetchall()
        else:
            return self.getEmployeeProducts(master, info)

    def getEmployeeProducts(self, master, info):
        """Get the products list from the employee's store"""

        cursor.execute(getEmployeeProductBase, (info['store_id'],))
        return cursor.fetchall()

    def placeReorder(self, master, info):
        """Update databse when reorder is placed"""

        if askyesno(title="Reorder Confirmation", message="Are you sure you want to place a reorder for this item?"):
            # Genereate a unique reorder ID
            cursor.execute("SELECT count(reorder_id) FROM reorder")
            reorderLen = cursor.fetchall()[0][0]
            reorderId = f"R{info['store_id']}{reorderLen}"
            qty = self.entries[info['entry_index']].get()

            # If information is valid, then update database
            if qty.isdigit() and int(qty) > 0 and int(qty) <= info['carries_quantity']:
                cursor.execute("INSERT INTO reorder VALUES (%s, %s, %s, %s, %s)",
                               (reorderId, info['store_id'], info['pid'], info['warehouse_id'], int(qty)))
                db.commit()

                if self.warning1: self.warning1.destroy()
                if self.warning2: self.warning2.destroy()
                self.success = tk.Label(self, text=f'Successfully placed reorder for {info["pname"]}', fg='green')
                self.success.grid(row=8, column=1, columnspan=2)
            elif qty.isdigit() and int(qty) > info['carries_quantity']: # Raise a warning in case of insufficient supply
                if self.success: self.success.destroy()
                if self.warning1: self.warning1.destroy()
                self.warning2 = tk.Label(self, text='Insufficient warehouse supply', fg='red')
                self.warning2.grid(row=8, column=1, columnspan=2)
            else:   # Raise a warning in case of invalid input
                if self.success: self.success.destroy()
                if self.warning2: self.warning2.destroy()
                self.warning1 = tk.Label(self, text='Invalid Quantity', fg='red')
                self.warning1.grid(row=8, column=1, columnspan=2)

class EmployeeSales(tk.Frame):
    def __init__(self, master, info=None):
        tk.Frame.__init__(self, master)
        tk.Label(self, text="Sales").grid(row=1, column=1, columnspan=2)
        tk.Button(self, text="Back", fg='blue',
                  command=lambda: master.switch_frame(EmployeeHome, info)).grid(row=5, column=1, columnspan=2, pady=5)

        # Display all sales in a scrollable list
        sales = ScrollableFrame(self)
        sortedSales = sorted(self.getSales(), key=lambda x: x[2])
        for sale in sortedSales:
            f = tk.Frame(sales.scrollable_frame)
            newInfo = dict(info)
            newInfo['sale_id'] = sale[0]

            # Display sale information
            tk.Label(f, text=f'{sale[2]}', padx=10, width=15).pack(side="left")
            tk.Label(f, text=f'${sale[1]}', padx=10, width=7).pack(side="left")

            # Display all items of the sale in a drop-down list
            cursor.execute(
                "SELECT pname, price, cart_quantity FROM sales_cart NATURAL INNER JOIN cart NATURAL INNER JOIN products WHERE sale_id=%s",
                (sale[0],))
            items = [f'{i[0]}  ${i[1]}  Qty:{i[2]}' for i in cursor.fetchall()]
            print(items)
            clicked_item = tk.StringVar()
            if len(items):
                clicked_item.set(items[0])
            else:
                items = ['']
            drop = tk.OptionMenu(f, clicked_item, *items)
            drop.pack(side='left')

            f.pack()
        sales.grid(row=2, column=1)

    def getSales(self):
        """Returns all sales"""

        cursor.execute("SELECT * FROM Sales")
        return cursor.fetchall()

class EmployeeReorders(tk.Frame):
    def __init__(self, master, info=None):
        tk.Frame.__init__(self, master)
        tk.Label(self, text="Reorders").grid(row=1, column=1, columnspan=2)
        tk.Button(self, text="Back", fg='blue',
                  command=lambda: master.switch_frame(EmployeeHome, info)).grid(row=6, column=1, columnspan=2, pady=5)

        # Display all pending reorders
        reorders = ScrollableFrame(self)
        for order in self.getReorders(info):
            f = tk.Frame(reorders.scrollable_frame)

            # Store relevant information to pass along
            newInfo = dict(info)
            newInfo['warehouse_id'] = order[3]
            newInfo['reorder_id'] = order[1]
            newInfo['pid'] = order[0]
            newInfo['qty'] = order[4]

            # Display relevant information
            tk.Label(f, text=order[5], padx=10, width=20).pack(side="left")
            tk.Label(f, text=f"${order[6]}", padx=10, width=7).pack(side="left")
            tk.Label(f, text=f'Qty: {order[4]}', padx=10, width=5).pack(side="left")
            tk.Label(f, text=f'Warehouse ID: {order[3]}', padx=10, width=15).pack(side="left")
            tk.Button(f, text="Order Arrived", padx=10, fg="green", width=10,
                      command=lambda i=newInfo: self.fulfillReorder(master, i)).pack(side="left")
            f.pack()

        reorders.grid(row=2, column=1)

        # Display success message after a reorder is placed
        try:
            if info['reorder'] == 'successful':
                tk.Label(self, text="Reorder has been fulfilled, database successfully updated", fg='green').grid(row=5,
                                                                                                                  column=1)
                info['reorder'] = ""
        except:
            info['reorder'] = ''

    def getReorders(self, info):
        """Get current pending reorders from the employee's store"""

        cursor.execute("SELECT * FROM reorder NATURAL INNER JOIN products WHERE store_id=%s", (info['store_id'],))
        return cursor.fetchall()

    def fulfillReorder(self, master, info):
        """Update database if reorder is fulfilled"""

        if askyesno(title="Reorder Fulfillment Confirmation",
                    message="Are you sure you want to mark this order as arrived?"):
            cursor.execute(
                "UPDATE inventory SET inventory_quantity = inventory_quantity+%s WHERE pid=%s AND store_id=%s",
                (info['qty'], info['pid'], info['store_id']))
            db.commit()

            cursor.execute("UPDATE carries SET carries_quantity = carries_quantity-%s WHERE pid=%s AND warehouse_id=%s",
                           (info['qty'], info['pid'], info['warehouse_id']))
            db.commit()

            cursor.execute("DELETE FROM reorder WHERE reorder_id=%s", (info['reorder_id'],))
            db.commit()

            info['reorder'] = 'successful'
            master.switch_frame(EmployeeReorders, info)


#All relevant Customer Pages
class CustomerHome(tk.Frame):
    def __init__(self, master, info=None):
        tk.Frame.__init__(self, master)

        tk.Label(self, text=f"Welcome {info['name']}!").grid(row=1, column=1, columnspan=2)
        tk.Label(self, text=f"Balance: {self.getCredit(info)}").grid(row=2, column=1, padx=4, pady=4, )

        # Customer Menu Options
        tk.Button(self, text="Browse\nProducts", width=8, height=2,
                  command=lambda: master.switch_frame(CustomerBrowse, info)).grid(row=3, column=1, columnspan=1, padx=3,
                                                                                  pady=3)
        tk.Button(self, text="Cart", width=8, height=2,
                  command=lambda: master.switch_frame(CustomerCart, info)).grid(row=3, column=2, columnspan=1, padx=3,
                                                                                pady=3)
        tk.Button(self, text="Order\nHistory", width=8, height=2,
                  command=lambda: master.switch_frame(CustomerOrders, info)).grid(row=4, column=1, columnspan=2, padx=3,
                                                                                  pady=3)
        tk.Button(self, text="Logout", fg='red',
                  command=lambda: master.switch_frame(Login)).grid(row=5, column=1, columnspan=2, pady=5)

    def getCredit(self, info):
        """Gets the customer current balance"""

        cursor.execute(getCustomerBalance, (info['customer_id'],))
        result = cursor.fetchall()

        if len(result) == 0:
            return "N/A"
        else:
            return f'${result[0][0]}'

class CustomerBrowse(tk.Frame):
    def __init__(self, master, info=None):
        tk.Frame.__init__(self, master)
        tk.Label(self, text="Browse Products").grid(row=1, column=1, columnspan=2)
        tk.Button(self, text="Back", fg='blue',
                  command=lambda: master.switch_frame(CustomerHome, info)).grid(row=10, column=1, columnspan=2, pady=5)

        # Initialize warning variables
        self.success = None
        self.warning1 = None
        self.warning2 = None

        # Set sorting variables
        info.setdefault('sortName', 0)
        info.setdefault('sortCategory', 0)
        info.setdefault('sortPrice', 0)
        self.sortCategory = tk.IntVar(value=info['sortCategory'])
        self.sortName = tk.IntVar(value=info['sortName'])
        self.sortPrice = tk.IntVar(value=info['sortPrice'])

        # Display categories to filter by in a drop-down menu
        tk.Label(self, text='Filter By:').grid(row=4, column=1)
        info.setdefault('filterCategory', 'All Categories')
        cursor.execute("SELECT category FROM categories")
        db_categories = [i[0] for i in cursor.fetchall()]
        db_categories.insert(0, "All Categories")
        self.clicked_category = tk.StringVar()
        self.clicked_category.set(info['filterCategory'])
        drop = tk.OptionMenu(self, self.clicked_category, *db_categories)
        drop.grid(row=5, column=1)
        tk.Button(self, text='Apply Filter', command=lambda: self.applyFilter(master, info)).grid(row=6, column=1)

        products = ScrollableFrame(self, width=500)
        productList = self.filterList(master, info)

        # Apply selected sorting options
        info.setdefault('sortOn', [])
        if self.sortCategory.get():
            info['sortOn'].append("x[3]")
        else:
            try:
                info['sortOn'].remove('x[3]')
            except:
                print()
        if self.sortName.get():
            info['sortOn'].append("x[1]")
        else:
            try:
                info['sortOn'].remove('x[1]')
            except:
                print()
        if self.sortPrice.get():
            info['sortOn'].append("x[2]")
        else:
            try:
                info['sortOn'].remove('x[2]')
            except:
                print()
        if len(info['sortOn']): eval(f'productList.sort(key=lambda x: ({",".join(info["sortOn"])}))')

        # Display available products to customer
        self.entries = []
        for i in range(len(productList)):
            product = productList[i]
            f = tk.Frame(products.scrollable_frame)

            # Store relevant information to pass along
            newInfo = dict(info)
            newInfo['pid'] = product[0]
            newInfo['entry_index'] = i

            # Display relevant information
            tk.Label(f, text=product[3], padx=10, width=15).pack(side="left")
            tk.Label(f, text=product[1], padx=20, width=20).pack(side="left")
            tk.Label(f, text=f"${product[2]}", padx=10, width=7).pack(side="left")
            self.entries.append(tk.Entry(f, width=3))
            self.entries[-1].pack(side="left")
            tk.Button(f, text="Add to Cart", padx=10, width=10,
                      command=lambda i=newInfo: self.addToCart(master, i)).pack(side="left")
            f.pack()
        products.grid(row=2, column=1, columnspan=2)
        print(self.getCustomerProducts(master, info))

        # Buttons for sorting options
        tk.Checkbutton(self, text="Category", variable=self.sortCategory, onvalue=1, offvalue=0,
                       command=lambda: master.switch_frame(CustomerBrowse, self.updateItem(info, 'sortCategory',
                                                                                           not info[
                                                                                               'sortCategory']))).grid(
            row=5, column=2)
        tk.Checkbutton(self, text="Name", variable=self.sortName, onvalue=1, offvalue=0,
                       command=lambda: master.switch_frame(CustomerBrowse, self.updateItem(info, 'sortName',
                                                                                           not info['sortName']))).grid(
            row=6, column=2)
        tk.Checkbutton(self, text="Price", variable=self.sortPrice, onvalue=1, offvalue=0,
                       command=lambda: master.switch_frame(CustomerBrowse, self.updateItem(info, 'sortPrice', not info[
                           'sortPrice']))).grid(row=7, column=2)
        tk.Label(self, text="Sort By: ").grid(row=4, column=2)

    def updateItem(self, d, key, value):
        """Updates dictionary inline"""

        x = dict(d)
        x[key] = value
        return x

    def applyFilter(self, master, info):
        """Applies selected filter options"""

        info['filterCategory'] = self.clicked_category.get()
        master.switch_frame(CustomerBrowse, info)

    def filterList(self, master, info):
        """Filters product list based on selected options"""

        if info['filterCategory'] != "All Categories":
            cursor.execute(f"SELECT * FROM ({getCustomerProductsBase}) a WHERE a.category=%s",
                           (info['filterCategory'],))
            return cursor.fetchall()
        else:
            return self.getCustomerProducts(master, info)

    def getCustomerProducts(self, master, info):
        """Gets list of products"""

        cursor.execute(getCustomerProductsBase)
        return cursor.fetchall()

    def addToCart(self, master, info):
        """Adds an item to the customer's cart"""

        qty = self.entries[info['entry_index']].get()
        print(info['entry_index'], info['pid'])
        if qty.isdigit() and int(qty) > 0:
            try: # Add item to cart
                cursor.execute(addItemToCart, (info['customer_id'], info['pid'], int(qty)))
                db.commit()
                if self.warning1: self.warning1.destroy()
                if self.warning2: self.warning2.destroy()
                self.success = tk.Label(self, text='Successfully added item to cart', fg='green')
                self.success.grid(row=8, column=1, columnspan=2)
            except: # Warning if the item is already in the cart
                if self.success: self.success.destroy()
                if self.warning2: self.warning2.destroy()
                self.warning1 = tk.Label(self, text='Item is already in cart', fg='red')
                self.warning1.grid(row=8, column=1, columnspan=2)
        else: # Warning if invalid input
            if self.success: self.success.destroy()
            if self.warning1: self.warning1.destroy()
            self.warning2 = tk.Label(self, text='Invalid Quantity', fg='red')
            self.warning2.grid(row=8, column=1, columnspan=2)

class CustomerCart(tk.Frame):
    def __init__(self, master, info=None):
        tk.Frame.__init__(self, master)
        tk.Label(self, text="Cart").grid(row=1, column=1, columnspan=2)
        tk.Button(self, text="Back", fg='blue',
                  command=lambda: master.switch_frame(CustomerHome, info)).grid(row=6, column=1, columnspan=2, pady=5)

        #Diaplay all items in the cart
        cart = ScrollableFrame(self)
        cartSubtotal = 0
        print(self.currTempCart(info))
        for item in self.currTempCart(info):
            f = tk.Frame(cart.scrollable_frame)
            newInfo = dict(info)
            newInfo['pid'] = item[0]

            tk.Label(f, text=item[3], padx=10, width=20).pack(side="left")
            tk.Label(f, text=item[2], padx=10, width=5).pack(side="left")
            tk.Label(f, text=f"${item[4]}", padx=10, width=7).pack(side="left")
            itemTotal = item[4] * item[2]
            cartSubtotal += itemTotal
            tk.Label(f, text=f'${itemTotal}', padx=10, width=7).pack(side="left")
            tk.Button(f, text="remove", padx=10, fg="red", width=10,
                      command=lambda i=newInfo: self.removeItem(master, i)).pack(side="left")
            f.pack()
        cart.grid(row=2, column=1)
        tk.Label(self, text=f"Subtotal: ${cartSubtotal}", fg="green").grid(row=3, column=1)

        # Display confirmation/warning messages
        try:
            if info['transaction'] == 'successful':
                tk.Label(self, text="Purchase has successfully been made", fg='green').grid(row=5, column=1)
                info['transaction'] = ""
            elif info['transaction'] == 'No items':
                tk.Label(self, text="No items to purchase", fg='red').grid(row=5, column=1)
                info['transaction'] = ""
            elif info['transaction'] == 'insufficient funds':
                tk.Label(self, text="Insufficient funds for purchase", fg='red').grid(row=5, column=1)
                info['transaction'] = ""
        except:
            print()

        # Proceed to checkout button
        info['subtotal'] = cartSubtotal
        tk.Button(self, text="Proceed to Checkout",
                  command=lambda i=info: master.switch_frame(CustomerCheckOut, i)).grid(row=4, column=1)

    def currTempCart(self, info):
        """Returns all items in cart"""

        cursor.execute(getTempCart, (info['customer_id'],))
        return cursor.fetchall()

    def removeItem(self, master, info):
        """Removes an item from the cart"""

        confirm = askyesno(title="Confirmation", message="Are you sure you want to remove this item from your cart?")
        print(info)
        if confirm:
            cursor.execute(removeTempCartItem, (info['customer_id'], info['pid']))
            db.commit()
            master.switch_frame(CustomerCart, info)

class CustomerCheckOut(tk.Frame):
    def __init__(self, master, info=None):
        tk.Frame.__init__(self, master)
        tk.Label(self, text="Check Out").grid(row=1, column=1, columnspan=2)
        tk.Button(self, text="Back", fg='blue',
                  command=lambda: master.switch_frame(CustomerCart, info)).grid(row=5, column=1, columnspan=2, pady=5)

        # Order information
        tk.Label(self, text=f"Current Balance: {self.getCredit(info)}").grid(row=1, column=1, columnspan=2)
        tk.Label(self, text=f"Subtotal: ${info['subtotal']}").grid(row=2, column=1, columnspan=2)

        # List of addresses in a drop-down menu
        tk.Label(self, text='Shipping Address:').grid(row=3, column=1)
        cursor.execute(
            "SELECT street, city, state, zipcode, address_id FROM customer NATURAL INNER JOIN customer_address NATURAL INNER JOIN address WHERE customer_id = %s",
            (info['customer_id'],))
        self.db_addressesId = [f'{i[4]}:{i[0]}, {i[1]} {i[2]}, {i[3]}' for i in cursor.fetchall()]
        db_addresses = [i.split(':')[1] for i in self.db_addressesId]
        self.clicked_address = tk.StringVar()
        self.clicked_address.set(db_addresses[0])
        drop = tk.OptionMenu(self, self.clicked_address, *db_addresses)
        drop.grid(row=3, column=2)

        # Place order button
        tk.Button(self, text="Place Order", command=lambda: self.placeOrder(master, info)).grid(row=4, column=1,
                                                                                                columnspan=2)

    def getCredit(self, info):
        """Gets the customer's current balance"""

        cursor.execute(getCustomerBalance, (info['customer_id'],))
        result = cursor.fetchall()

        if len(result) == 0:
            return "N/A"
        else:
            return f'${result[0][0]}'

    def placeOrder(self, master, info):
        """Places an order for all items in the cart"""

        confirm = askyesno(title="Purchase Confirmation",
                           message=f"Would you like to make a purchase of ${info['subtotal']}?")
        currentBalance = float(self.getCredit(info)[1:])
        sufficientFunds = float(info['subtotal']) <= currentBalance
        print(currentBalance, float(info['subtotal']), sufficientFunds)

        # Generate Ids
        cursor.execute("SELECT count(tracking_id) FROM online_orders")
        onlineOrdersLen = cursor.fetchall()[0][0]
        cursor.execute("SELECT count(customer_id) FROM temp_cart")
        cartLen = cursor.fetchall()[0][0]
        cursor.execute("SELECT count(sale_id) FROM sales")
        saleLen = cursor.fetchall()[0][0]

        if confirm and sufficientFunds and cartLen != 0:

            # Generate necessary IDs
            cartId = f"{info['customer_id']}{cartLen}"
            trackingId = f"{info['customer_id']}{onlineOrdersLen}"
            saleId = f"{info['customer_id']}{saleLen}"
            addressId = None
            print(self.db_addressesId)
            for address in self.db_addressesId:
                print(address)
                print(self.clicked_address.get())
                print('---')
                if self.clicked_address.get() in address:
                    addressId = address.split(":")[0]

            # Add items to cart
            cursor.execute("SELECT * FROM temp_cart WHERE customer_id=%s", (info['customer_id'],))
            currentTempCart = cursor.fetchall()
            for item in currentTempCart:
                print(cartId, item)
                cursor.execute(f"INSERT INTO cart VALUES (%s, %s, %s)", (cartId, item[1], item[2]))
                db.commit()

            # Subtract total from balance
            cursor.execute("SELECT credit_id FROM customer NATURAL INNER JOIN has_credit WHERE customer_id=%s",
                           (info['customer_id'],))
            getCustomerCreditId = cursor.fetchall()[0][0]
            cursor.execute("UPDATE credit SET balance = balance - %s WHERE credit_id = %s",
                           (info['subtotal'], getCustomerCreditId))
            db.commit()

            # Update Online Order and Online Cart
            cursor.execute(f"INSERT INTO online_orders VALUES (%s, %s)", (trackingId, addressId))
            db.commit()

            for item in currentTempCart:
                cursor.execute(f"INSERT INTO online_cart VALUES (%s, %s, %s)", (trackingId, cartId, item[1]))
                db.commit()

            # Update Sales and sales cart
            cursor.execute(f"INSERT INTO sales VALUES (%s, %s, CURRENT_TIMESTAMP())", (saleId, info['subtotal']))
            db.commit()

            for item in currentTempCart:
                cursor.execute(f"INSERT INTO sales_cart VALUES (%s, %s, %s)", (saleId, cartId, item[1]))
                db.commit()

            # Add transaction to order history
            cursor.execute("INSERT INTO order_history VALUES (%s, %s)", (info['customer_id'], trackingId))
            db.commit()

            # Delete all items in temp_cart
            cursor.execute("DELETE FROM temp_cart WHERE customer_id = %s", (info['customer_id'],))
            db.commit()

            info['transaction'] = 'successful'
            master.switch_frame(CustomerCart, info)
        elif not sufficientFunds:
            info['transaction'] = 'insufficient funds'
            master.switch_frame(CustomerCart, info)
        elif cartLen == 0:
            info['transaction'] = 'No items'
            master.switch_frame(CustomerCart, info)
        else:
            master.switch_frame(CustomerCart, info)

class CustomerOrders(tk.Frame):
    def __init__(self, master, info=None):
        tk.Frame.__init__(self, master)
        tk.Label(self, text="Order History").grid(row=1, column=1, columnspan=2)
        tk.Button(self, text="Back", fg='blue',
                  command=lambda: master.switch_frame(CustomerHome, info)).grid(row=5, column=1, columnspan=2, pady=5)

        # List all previous orders
        orders = ScrollableFrame(self)
        for order in self.getOrderHistory(info):
            f = tk.Frame(orders.scrollable_frame)

            print(order)
            # Necessary information to pass along
            newInfo = dict(info)
            newInfo['cart_id'] = order[1]
            newInfo['sale_id'] = order[0]
            newInfo['tracking_id'] = order[3]
            newInfo['address_id'] = order[5]
            newInfo['pid'] = order[2]
            newInfo['qty'] = order[6]
            print(newInfo['pid'])
            productInfo = self.getProductName(newInfo)[0]
            addressName = self.getAddress(newInfo)[0]
            newInfo['price'] = productInfo[1]
            newInfo['pname'] = productInfo[0]

            # Display relevant information
            tk.Label(f, text=productInfo[0], padx=10, width=20).grid(row=1, column=1)
            tk.Label(f, text=f'qty: {newInfo["qty"]}', padx=10, width=8).grid(row=1, column=2)
            tk.Label(f, text=f"${productInfo[1]}", padx=10, width=7).grid(row=1, column=3)
            itemTotal = productInfo[1] * newInfo['qty']
            tk.Label(f, text=f'Total: ${itemTotal}', padx=10, width=15).grid(row=1, column=4)
            tk.Button(f, text="Return Item", padx=10, fg="red", width=10,
                      command=lambda i=newInfo: self.returnItem(master, i)).grid(row=1, column=6, rowspan=2)

            tk.Label(f, text=order[8], padx=10, width=15).grid(row=2, column=2)
            tk.Label(f, text=f"{addressName[0]}, {addressName[1]} {addressName[2]}, {addressName[3]}").grid(row=2,
                                                                                                            column=1)
            f.pack()
        orders.grid(row=2, column=1)

        # Display confirmation message
        try:
            if info['return'] == 'successful':
                tk.Label(self, text=f'Successfully returned {info["qty"]} {info["pname"]}(s)', fg='green').grid(row=3,
                                                                                                                column=1)
                info['return'] = ''
        except:
            info['return'] = ''

    def getOrderHistory(self, info):
        """Get all previously ordered items"""

        cursor.execute(getCustomerOrderHistory, (info['customer_id'],))
        return cursor.fetchall()

    def getProductName(self, info):
        """Get a product information for a given product id"""

        cursor.execute("SELECT pname, price FROM products WHERE pid = %s", (info['pid'],))
        return cursor.fetchall()

    def getAddress(self, info):
        """Get address information from a give address id"""

        cursor.execute("SELECT street, city, state, zipcode FROM address WHERE address_id = %s", (info['address_id'],))
        return cursor.fetchall()

    def returnItem(self, master, info):
        """Returns an item and refunds the customer"""

        confirm = askyesno(title='Return Confirmation', message=f"Are you sure you want to return {info['pname']}?")

        if confirm:
            # Add money back to balance

            cursor.execute("SELECT credit_id FROM customer NATURAL INNER JOIN has_credit WHERE customer_id=%s",
                           (info['customer_id'],))
            getCustomerCreditId = cursor.fetchall()[0][0]

            cursor.execute("UPDATE credit SET balance = balance + %s WHERE credit_id = %s",
                           ((info['price'] * info['qty']), getCustomerCreditId))
            db.commit()

            # delete from cart, making sure not empty

            cursor.execute("DELETE FROM online_cart WHERE cart_id=%s and tracking_id=%s and pid=%s",
                           (info['cart_id'], info['tracking_id'], info['pid']))
            db.commit()
            cursor.execute("DELETE FROM sales_cart WHERE cart_id=%s and sale_id=%s and pid=%s",
                           (info['cart_id'], info['sale_id'], info['pid']))
            db.commit()
            cursor.execute("DELETE FROM cart WHERE cart_id=%s and pid=%s", (info['cart_id'], info['pid']))
            db.commit()

            info['return'] = 'successful'
            master.switch_frame(CustomerOrders, info)
        else:
            master.switch_frame(CustomerOrders, info)


# Run application
app = Application()
app.mainloop()
