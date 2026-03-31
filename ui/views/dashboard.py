from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
try:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

class DashboardView(QWidget):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(self.layout)
        
        title = QLabel("Overview Dashboard")
        title.setStyleSheet("font-size: 28px; font-weight: bold; margin: 10px;")
        self.layout.addWidget(title)
        
        # Stats Cards Layout
        self.stats_layout = QHBoxLayout()
        self.layout.addLayout(self.stats_layout)
        
        self.total_items_label = self._create_card("Total Unique Items", "0")
        self.total_stock_label = self._create_card("Total Stock Units", "0")
        self.low_stock_label = self._create_card("Low Stock Alerts", "0")
        
        self.chart_container = QVBoxLayout()
        self.layout.addLayout(self.chart_container)

        self.refresh()
        
    def _create_card(self, title, value):
        card = QWidget()
        card.setProperty("class", "Card")
        l = QVBoxLayout()
        card.setLayout(l)
        
        t = QLabel(title)
        t.setStyleSheet("color: #A6ADC8; font-size: 14px;")
        
        v = QLabel(value)
        v.setStyleSheet("color: #89B4FA; font-size: 32px; font-weight: bold;")
        v.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        l.addWidget(t)
        l.addWidget(v)
        
        self.stats_layout.addWidget(card)
        return v
        
    def refresh(self):
        items = self.manager.get_all_items()
        
        total_items = len(items)
        total_stock = sum(item.stock for item in items)
        low_stock = len(self.manager.get_low_stock_items(10))
        
        self.total_items_label.setText(str(total_items))
        self.total_stock_label.setText(str(total_stock))
        self.low_stock_label.setText(str(low_stock))
        
        if HAS_MATPLOTLIB and items:
            self._draw_chart(items)
        elif not HAS_MATPLOTLIB:
            lbl = QLabel("Please `pip install matplotlib` to view charts.")
            self.chart_container.addWidget(lbl)

    def _draw_chart(self, items):
        # Clear previous chart
        for i in reversed(range(self.chart_container.count())): 
            widget = self.chart_container.itemAt(i).widget()
            if widget:
                widget.setParent(None)
                
        fig = Figure(figsize=(6, 4), dpi=100)
        fig.patch.set_facecolor('#1E1E2E')
        
        ax = fig.add_subplot(111)
        ax.set_facecolor('#1E1E2E')
        ax.tick_params(colors='#CDD6F4')
        for spine in ax.spines.values():
            spine.set_color('#45475A')
            
        categories = {}
        for item in items:
            categories[item.category] = categories.get(item.category, 0) + item.stock
            
        labels = list(categories.keys())
        values = list(categories.values())
        
        if not labels:
            return
            
        ax.bar(labels, values, color='#CBA6F7')
        ax.set_title('Stock Available by Category', color='#CDD6F4', pad=20)
        ax.set_ylabel('Total Stock', color='#CDD6F4')
        
        canvas = FigureCanvas(fig)
        self.chart_container.addWidget(canvas)
