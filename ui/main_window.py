from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget
from PyQt6.QtCore import Qt
from core import InventoryManager

# Import views
from ui.views.dashboard import DashboardView
from ui.views.inventory_view import InventoryView
from ui.views.orders_page import OrdersView
from ui.views.reports_page import ReportsView
from ui.views.users_page import UsersView

class MainWindow(QMainWindow):
    def __init__(self, current_user):
        super().__init__()
        self.current_user = current_user
        
        role = current_user[3].capitalize() if current_user else "User"
        username = current_user[1] if current_user else "Unknown"
        self.setWindowTitle(f"Pro Inventory Manager - Logged in as: {username} ({role})")
        self.setMinimumSize(1100, 750)
        
        self.manager = InventoryManager(current_user)
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        main_widget.setLayout(layout)
        
        # Sidebar
        self.sidebar = QWidget()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(240)
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        sidebar_layout.setContentsMargins(0, 20, 0, 0)
        self.sidebar.setLayout(sidebar_layout)
        
        # Stacked Widget
        self.content = QStackedWidget()
        
        # Initialize Views
        self.dashboard_view = DashboardView(self.manager)
        self.inventory_view = InventoryView(self.manager)
        self.orders_view = OrdersView(self.manager)
        self.reports_view = ReportsView(self.manager)
        
        self.content.addWidget(self.dashboard_view)
        self.content.addWidget(self.inventory_view)
        self.content.addWidget(self.orders_view)
        self.content.addWidget(self.reports_view)
        
        # Buttons Setup
        self.add_nav_btn("📊 Dashboard", 0, sidebar_layout)
        self.add_nav_btn("📦 Inventory Mgmt", 1, sidebar_layout)
        self.add_nav_btn("🛒 Orders & RESTOCK", 2, sidebar_layout)
        self.add_nav_btn("📈 Data & Reports", 3, sidebar_layout)
        
        # Explicit Admin Role Check
        if self.manager.current_role == 'admin':
            self.users_view = UsersView(self.manager)
            self.content.addWidget(self.users_view)
            self.add_nav_btn("👥 User Management", 4, sidebar_layout)
        
        layout.addWidget(self.sidebar)
        layout.addWidget(self.content)
        
        self.content.currentChanged.connect(self.on_tab_changed)

    def add_nav_btn(self, text, index, layout):
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        if index == 0:
            btn.setChecked(True)
        
        btn.clicked.connect(lambda: self.switch_tab(index, btn))
        layout.addWidget(btn)
        
    def switch_tab(self, index, button):
        self.content.setCurrentIndex(index)
        for i in range(self.sidebar.layout().count()):
            widget = self.sidebar.layout().itemAt(i).widget()
            if isinstance(widget, QPushButton):
                widget.setChecked(widget == button)
                
    def on_tab_changed(self, index):
        if index == 0:
            self.dashboard_view.refresh()
        elif index == 1:
            self.inventory_view.refresh()
        elif index == 2:
            self.orders_view.refresh()
        elif index == 3:
            self.reports_view.refresh()
        elif index == 4:
            self.users_view.refresh()
