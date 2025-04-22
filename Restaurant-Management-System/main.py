import streamlit as st
import uuid
from datetime import datetime
import json
import os

# Define core classes for the Restaurant Management System

class MenuItem:
    def __init__(self, name, price, category, ingredients=None):
        self.id = str(uuid.uuid4())
        self.name = name
        self.price = price
        self.category = category
        self.ingredients = ingredients if ingredients else {}
        self.available = True
    
    def update_price(self, new_price):
        self.price = new_price
    
    def check_availability(self, inventory):
        for ingredient, required_qty in self.ingredients.items():
            if ingredient not in inventory or inventory[ingredient].quantity < required_qty:
                self.available = False
                return False
        self.available = True
        return True
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "category": self.category,
            "ingredients": self.ingredients,
            "available": self.available
        }
    
    @classmethod
    def from_dict(cls, data):
        item = cls(data["name"], data["price"], data["category"], data["ingredients"])
        item.id = data["id"]
        item.available = data["available"]
        return item


class InventoryItem:
    def __init__(self, name, quantity, unit, reorder_level=10):
        self.id = str(uuid.uuid4())
        self.name = name
        self.quantity = quantity
        self.unit = unit
        self.reorder_level = reorder_level
    
    def update_quantity(self, amount):
        self.quantity += amount
        
    def needs_reorder(self):
        return self.quantity <= self.reorder_level
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "quantity": self.quantity,
            "unit": self.unit,
            "reorder_level": self.reorder_level
        }
    
    @classmethod
    def from_dict(cls, data):
        item = cls(data["name"], data["quantity"], data["unit"], data["reorder_level"])
        item.id = data["id"]
        return item


class Order:
    def __init__(self, customer_name, table_number):
        self.id = str(uuid.uuid4())
        self.customer_name = customer_name
        self.table_number = table_number
        self.items = []  # List of (MenuItem, quantity) tuples
        self.timestamp = datetime.now()
        self.status = "pending"  # pending, preparing, served, paid
        self.total = 0
    
    def add_item(self, menu_item, quantity):
        # Check if item already exists in order
        for i, (item, qty) in enumerate(self.items):
            if item.id == menu_item.id:
                self.items[i] = (item, qty + quantity)
                self.calculate_total()
                return
        
        self.items.append((menu_item, quantity))
        self.calculate_total()
    
    def remove_item(self, menu_item_id):
        self.items = [(item, qty) for item, qty in self.items if item.id != menu_item_id]
        self.calculate_total()
    
    def update_status(self, new_status):
        self.status = new_status
    
    def calculate_total(self):
        self.total = sum(item.price * qty for item, qty in self.items)
        return self.total
    
    def to_dict(self):
        return {
            "id": self.id,
            "customer_name": self.customer_name,
            "table_number": self.table_number,
            "items": [(item.id, qty) for item, qty in self.items],
            "timestamp": self.timestamp.isoformat(),
            "status": self.status,
            "total": self.total
        }


class Restaurant:
    def __init__(self):
        self.menu = {}  # id -> MenuItem
        self.inventory = {}  # name -> InventoryItem
        self.orders = {}  # id -> Order
        self.load_data()
    
    def add_menu_item(self, menu_item):
        self.menu[menu_item.id] = menu_item
        self.save_data()
    
    def update_menu_item(self, menu_item):
        if menu_item.id in self.menu:
            self.menu[menu_item.id] = menu_item
            self.save_data()
    
    def remove_menu_item(self, item_id):
        if item_id in self.menu:
            del self.menu[item_id]
            self.save_data()
    
    def add_inventory_item(self, inventory_item):
        self.inventory[inventory_item.name] = inventory_item
        self.save_data()
    
    def update_inventory(self, item_name, amount):
        if item_name in self.inventory:
            self.inventory[item_name].update_quantity(amount)
            self.save_data()
    
    def create_order(self, order):
        self.orders[order.id] = order
        self.save_data()
    
    def update_order_status(self, order_id, status):
        if order_id in self.orders:
            self.orders[order_id].update_status(status)
            self.save_data()
    
    def get_menu_items_by_category(self):
        categories = {}
        for item in self.menu.values():
            if item.category not in categories:
                categories[item.category] = []
            categories[item.category].append(item)
        return categories
    
    def process_order(self, order_id):
        if order_id not in self.orders:
            return False
        
        order = self.orders[order_id]
        
        # Deduct ingredients from inventory
        for menu_item, quantity in order.items:
            for ingredient, amount in menu_item.ingredients.items():
                if ingredient in self.inventory:
                    self.inventory[ingredient].update_quantity(-amount * quantity)
        
        order.update_status("preparing")
        self.save_data()
        return True
    
    def update_menu_availability(self):
        for item in self.menu.values():
            item.check_availability(self.inventory)
        self.save_data()
    
    def get_inventory_alerts(self):
        return [item for item in self.inventory.values() if item.needs_reorder()]
    
    def load_data(self):
        try:
            if os.path.exists("menu.json"):
                with open("menu.json", "r") as f:
                    menu_data = json.load(f)
                    self.menu = {item_id: MenuItem.from_dict(data) for item_id, data in menu_data.items()}
            
            if os.path.exists("inventory.json"):
                with open("inventory.json", "r") as f:
                    inventory_data = json.load(f)
                    self.inventory = {name: InventoryItem.from_dict(data) for name, data in inventory_data.items()}
        except Exception as e:
            print(f"Error loading data: {e}")
    
    def save_data(self):
        try:
            menu_data = {item_id: item.to_dict() for item_id, item in self.menu.items()}
            with open("menu.json", "w") as f:
                json.dump(menu_data, f, indent=2)
            
            inventory_data = {item.name: item.to_dict() for item in self.inventory.values()}
            with open("inventory.json", "w") as f:
                json.dump(inventory_data, f, indent=2)
            
            # Save only active orders
            active_orders = {order_id: order.to_dict() for order_id, order in self.orders.items() 
                            if order.status != "paid"}
            with open("orders.json", "w") as f:
                json.dump(active_orders, f, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")


# Streamlit UI
class RestaurantUI:
    def __init__(self):
        self.restaurant = Restaurant()
        
    def run(self):
        st.title("🍽️ Restaurant Management System")
        
        # Initialize session state if not already done
        if "active_tab" not in st.session_state:
            st.session_state.active_tab = "Menu"
        
        # Sidebar navigation
        st.sidebar.title("Navigation")
        tab = st.sidebar.radio("Select Section", 
                            ["Menu", "Inventory", "Orders", "Reports"])
        st.session_state.active_tab = tab
        
        # Display the appropriate tab
        if st.session_state.active_tab == "Menu":
            self.menu_management()
        elif st.session_state.active_tab == "Inventory":
            self.inventory_management()
        elif st.session_state.active_tab == "Orders":
            self.order_management()
        elif st.session_state.active_tab == "Reports":
            self.reports()
    
    def menu_management(self):
        st.header("Menu Management")
        
        tab1, tab2 = st.tabs(["View Menu", "Add/Edit Item"])
        
        with tab1:
            categories = self.restaurant.get_menu_items_by_category()
            if not categories:
                st.info("No menu items available. Add some items to get started!")
            else:
                for category, items in categories.items():
                    st.subheader(category)
                    for item in items:
                        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                        status = "✅" if item.available else "❌"
                        with col1:
                            st.write(f"{item.name}")
                        with col2:
                            st.write(f"${item.price:.2f}")
                        with col3:
                            st.write(status)
                        with col4:
                            if st.button("Delete", key=f"del_{item.id}"):
                                self.restaurant.remove_menu_item(item.id)
                                st.rerun()
                    st.divider()
        
        with tab2:
            st.subheader("Add/Edit Menu Item")
            name = st.text_input("Item Name")
            price = st.number_input("Price", min_value=0.0, step=0.5, format="%.2f")
            category = st.selectbox("Category", ["Appetizer", "Main Course", "Dessert", "Beverage"])
            
            # Dynamic ingredient selection
            st.subheader("Ingredients")
            ingredients = {}
            
            # Get existing inventory items for selection
            inventory_items = list(self.restaurant.inventory.keys())
            
            if inventory_items:
                cols = st.columns(2)
                with cols[0]:
                    selected_ingredient = st.selectbox("Select Ingredient", inventory_items)
                with cols[1]:
                    qty = st.number_input("Quantity", min_value=0.1, step=0.1, format="%.1f")
                
                if st.button("Add Ingredient"):
                    # Add to temporary dict
                    if "temp_ingredients" not in st.session_state:
                        st.session_state.temp_ingredients = {}
                    
                    st.session_state.temp_ingredients[selected_ingredient] = qty
                    st.rerun()
                
                # Display added ingredients
                if "temp_ingredients" in st.session_state and st.session_state.temp_ingredients:
                    st.write("Added ingredients:")
                    for ing, q in st.session_state.temp_ingredients.items():
                        st.write(f"- {ing}: {q} {self.restaurant.inventory[ing].unit if ing in self.restaurant.inventory else ''}")
                    
                    ingredients = st.session_state.temp_ingredients.copy()
                    
                    if st.button("Clear Ingredients"):
                        st.session_state.temp_ingredients = {}
                        st.rerun()
            else:
                st.info("No inventory items available. Add some in the Inventory section.")
            
            if st.button("Save Menu Item"):
                if name and price > 0:
                    menu_item = MenuItem(name, price, category, ingredients)
                    menu_item.check_availability(self.restaurant.inventory)
                    self.restaurant.add_menu_item(menu_item)
                    
                    # Clear temp ingredients
                    if "temp_ingredients" in st.session_state:
                        st.session_state.temp_ingredients = {}
                    
                    st.success(f"Menu item '{name}' added successfully!")
                    st.rerun()
                else:
                    st.error("Please fill all required fields.")
    
    def inventory_management(self):
        st.header("Inventory Management")
        
        tab1, tab2 = st.tabs(["View Inventory", "Add/Update Item"])
        
        with tab1:
            if not self.restaurant.inventory:
                st.info("No inventory items available. Add some items to get started!")
            else:
                inventory_items = list(self.restaurant.inventory.values())
                
                # Create tables for normal and low stock
                low_stock = [item for item in inventory_items if item.needs_reorder()]
                normal_stock = [item for item in inventory_items if not item.needs_reorder()]
                
                if normal_stock:
                    st.subheader("Current Inventory")
                    for item in normal_stock:
                        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                        with col1:
                            st.write(f"{item.name}")
                        with col2:
                            st.write(f"{item.quantity:.1f} {item.unit}")
                        with col3:
                            st.write(f"Reorder at: {item.reorder_level}")
                        with col4:
                            if st.button("+", key=f"add_{item.name}"):
                                st.session_state.update_item = item.name
                                st.session_state.update_qty = 1.0
                                st.rerun()
                
                if low_stock:
                    st.subheader("Low Stock Items")
                    for item in low_stock:
                        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                        with col1:
                            st.write(f"⚠️ {item.name}")
                        with col2:
                            st.write(f"{item.quantity:.1f} {item.unit}")
                        with col3:
                            st.write(f"Reorder at: {item.reorder_level}")
                        with col4:
                            if st.button("+", key=f"add_low_{item.name}"):
                                st.session_state.update_item = item.name
                                st.session_state.update_qty = item.reorder_level * 2 - item.quantity
                                st.rerun()
        
        with tab2:
            if "update_item" in st.session_state:
                st.subheader(f"Update {st.session_state.update_item}")
                qty = st.number_input("Add Quantity", value=st.session_state.update_qty, step=1.0)
                
                if st.button("Add to Inventory"):
                    self.restaurant.update_inventory(st.session_state.update_item, qty)
                    self.restaurant.update_menu_availability()
                    st.success(f"Added {qty} {self.restaurant.inventory[st.session_state.update_item].unit} of {st.session_state.update_item}")
                    del st.session_state.update_item
                    del st.session_state.update_qty
                    st.rerun()
                
                if st.button("Cancel Update"):
                    del st.session_state.update_item
                    del st.session_state.update_qty
                    st.rerun()
            else:
                st.subheader("Add New Inventory Item")
                name = st.text_input("Item Name")
                quantity = st.number_input("Quantity", min_value=0.0, step=1.0)
                unit = st.selectbox("Unit", ["kg", "g", "l", "ml", "pcs", "bottles", "packages"])
                reorder_level = st.number_input("Reorder Level", min_value=1, step=1)
                
                if st.button("Add Item"):
                    if name and quantity >= 0:
                        inventory_item = InventoryItem(name, quantity, unit, reorder_level)
                        self.restaurant.add_inventory_item(inventory_item)
                        self.restaurant.update_menu_availability()
                        st.success(f"Inventory item '{name}' added successfully!")
                        st.rerun()
                    else:
                        st.error("Please fill all required fields.")
    
    def order_management(self):
        st.header("Order Management")
        
        tab1, tab2, tab3 = st.tabs(["New Order", "Active Orders", "Order History"])
        
        with tab1:
            st.subheader("Create New Order")
            
            customer_name = st.text_input("Customer Name")
            table_number = st.number_input("Table Number", min_value=1, step=1)
            
            # Only show available menu items
            available_items = [item for item in self.restaurant.menu.values() if item.available]
            
            if not available_items:
                st.warning("No menu items available. Please check inventory and add menu items.")
            else:
                if "current_order" not in st.session_state:
                    st.session_state.current_order = Order(customer_name if customer_name else "Guest", table_number)
                
                # Update customer info if changed
                st.session_state.current_order.customer_name = customer_name if customer_name else "Guest"
                st.session_state.current_order.table_number = table_number
                
                # Menu selection by category
                categories = {}
                for item in available_items:
                    if item.category not in categories:
                        categories[item.category] = []
                    categories[item.category].append(item)
                
                for category, items in categories.items():
                    with st.expander(f"{category} ({len(items)} items)"):
                        for item in items:
                            col1, col2, col3 = st.columns([3, 1, 1])
                            with col1:
                                st.write(f"{item.name} - ${item.price:.2f}")
                            with col2:
                                qty = st.number_input("Qty", min_value=1, max_value=20, value=1, step=1, key=f"qty_{item.id}")
                            with col3:
                                if st.button("Add", key=f"add_to_order_{item.id}"):
                                    st.session_state.current_order.add_item(item, qty)
                                    st.rerun()
                
                # Show current order
                if st.session_state.current_order.items:
                    st.subheader("Current Order")
                    for i, (item, qty) in enumerate(st.session_state.current_order.items):
                        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                        with col1:
                            st.write(f"{item.name}")
                        with col2:
                            st.write(f"x{qty}")
                        with col3:
                            st.write(f"${item.price * qty:.2f}")
                        with col4:
                            if st.button("Remove", key=f"remove_{i}"):
                                st.session_state.current_order.remove_item(item.id)
                                st.rerun()
                    
                    st.write(f"**Total: ${st.session_state.current_order.total:.2f}**")
                    
                    if st.button("Place Order"):
                        self.restaurant.create_order(st.session_state.current_order)
                        self.restaurant.process_order(st.session_state.current_order.id)
                        st.success("Order placed successfully!")
                        st.session_state.current_order = Order("Guest", table_number)
                        st.rerun()
                
                if st.button("Clear Order"):
                    st.session_state.current_order = Order("Guest", table_number)
                    st.rerun()
        
        with tab2:
            st.subheader("Active Orders")
            
            active_orders = [order for order in self.restaurant.orders.values() 
                             if order.status in ["pending", "preparing", "served"]]
            
            if not active_orders:
                st.info("No active orders at the moment.")
            else:
                for order in active_orders:
                    with st.expander(f"Order #{order.id[:8]} - Table {order.table_number} - {order.status.upper()}"):
                        st.write(f"Customer: {order.customer_name}")
                        st.write(f"Time: {order.timestamp.strftime('%H:%M:%S')}")
                        
                        for item, qty in order.items:
                            st.write(f"- {item.name} x{qty} (${item.price * qty:.2f})")
                        
                        st.write(f"**Total: ${order.total:.2f}**")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            if order.status == "pending" and st.button("Start Preparing", key=f"prep_{order.id}"):
                                self.restaurant.update_order_status(order.id, "preparing")
                                st.rerun()
                        with col2:
                            if order.status == "preparing" and st.button("Mark as Served", key=f"serve_{order.id}"):
                                self.restaurant.update_order_status(order.id, "served")
                                st.rerun()
                        with col3:
                            if order.status == "served" and st.button("Complete Order", key=f"complete_{order.id}"):
                                self.restaurant.update_order_status(order.id, "paid")
                                st.rerun()
        
        with tab3:
            st.subheader("Order History")
            
            completed_orders = [order for order in self.restaurant.orders.values() if order.status == "paid"]
            
            if not completed_orders:
                st.info("No completed orders in history.")
            else:
                for order in sorted(completed_orders, key=lambda x: x.timestamp, reverse=True):
                    with st.expander(f"Order #{order.id[:8]} - {order.timestamp.strftime('%Y-%m-%d %H:%M')}"):
                        st.write(f"Customer: {order.customer_name}")
                        st.write(f"Table: {order.table_number}")
                        
                        for item, qty in order.items:
                            st.write(f"- {item.name} x{qty} (${item.price * qty:.2f})")
                        
                        st.write(f"**Total: ${order.total:.2f}**")
    
    def reports(self):
        st.header("Reports & Analytics")
        
        # Summary statistics
        total_items = len(self.restaurant.menu)
        total_inventory = len(self.restaurant.inventory)
        total_orders = len([order for order in self.restaurant.orders.values() if order.status == "paid"])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Menu Items", total_items)
        with col2:
            st.metric("Inventory Items", total_inventory)
        with col3:
            st.metric("Completed Orders", total_orders)
        
        # Low inventory alerts
        low_stock = self.restaurant.get_inventory_alerts()
        if low_stock:
            st.subheader("⚠️ Low Stock Alerts")
            for item in low_stock:
                st.warning(f"{item.name}: {item.quantity:.1f} {item.unit} (Reorder level: {item.reorder_level})")
        
        # Daily sales report
        if self.restaurant.orders:
            st.subheader("Daily Sales Report")
            
            # Calculate daily sales
            today = datetime.now().date()
            daily_sales = sum(order.total for order in self.restaurant.orders.values() 
                             if order.status == "paid" and order.timestamp.date() == today)
            
            st.metric("Today's Sales", f"${daily_sales:.2f}")
            
            # Most popular items
            item_counts = {}
            for order in self.restaurant.orders.values():
                if order.status == "paid":
                    for item, qty in order.items:
                        if item.name in item_counts:
                            item_counts[item.name] += qty
                        else:
                            item_counts[item.name] = qty
            
            if item_counts:
                st.subheader("Popular Items")
                popular_items = sorted(item_counts.items(), key=lambda x: x[1], reverse=True)[:5]
                
                for item_name, count in popular_items:
                    st.write(f"- {item_name}: {count} orders")


if __name__ == "__main__":
    ui = RestaurantUI()
    ui.run()