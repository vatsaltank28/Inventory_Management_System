from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGraphicsDropShadowEffect, QComboBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
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
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setSpacing(25)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(self.layout)
        
        title = QLabel("Overview Dashboard")
        title.setObjectName("DashboardTitle")
        self.layout.addWidget(title)
        
        # Stats Cards Layout
        self.stats_layout = QHBoxLayout()
        self.stats_layout.setSpacing(20)
        self.layout.addLayout(self.stats_layout)
        
        self.total_items_label = self._create_card("Total Unique Items", "0")
        self.total_stock_label = self._create_card("Total Stock Units", "0")
        self.low_stock_label = self._create_card("Low Stock Alerts", "0")
        
        self.chart_container = QVBoxLayout()
        
        # Chart Controls
        chart_ctrl_layout = QHBoxLayout()
        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItems(["Bar Chart", "Donut Chart (Premium)"])
        self.chart_type_combo.setFixedWidth(200)
        self.chart_type_combo.currentIndexChanged.connect(self._force_redraw)
        chart_ctrl_layout.addStretch()
        chart_ctrl_layout.addWidget(self.chart_type_combo)
        self.chart_container.addLayout(chart_ctrl_layout)
        
        self.canvas_container = QVBoxLayout()
        self.chart_container.addLayout(self.canvas_container, stretch=1)
        
        self.layout.addLayout(self.chart_container, stretch=1)

        self.refresh()
        
    def _force_redraw(self):
        items = self.manager.get_all_items()
        if items and HAS_MATPLOTLIB:
            self._draw_chart(items)
        
    def _create_card(self, title, value):
        card = QWidget()
        card.setProperty("class", "Card")
        card.setMinimumHeight(140)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 4)
        card.setGraphicsEffect(shadow)
        
        l = QVBoxLayout()
        card.setLayout(l)
        
        t = QLabel(title)
        t.setObjectName("StatTitle")
        
        v = QLabel(value)
        v.setObjectName("StatValue")
        v.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        l.addWidget(t)
        l.addStretch()
        l.addWidget(v)
        l.addStretch()
        
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
        
        # Apply Alert style if items are low stock
        is_alert = "true" if low_stock > 0 else "false"
        self.low_stock_label.setProperty("Alert", is_alert)
        self.low_stock_label.style().unpolish(self.low_stock_label)
        self.low_stock_label.style().polish(self.low_stock_label)
        
        if HAS_MATPLOTLIB and items:
            self._draw_chart(items)
        elif not HAS_MATPLOTLIB:
            lbl = QLabel("Please `pip install matplotlib` to view charts.")
            self.canvas_container.addWidget(lbl)

    def _draw_chart(self, items):
        # Clear previous chart
        for i in reversed(range(self.canvas_container.count())): 
            widget = self.canvas_container.itemAt(i).widget()
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
            
        # Limit to top 4 categories, group the rest into 'Others'
        sorted_cats = sorted(categories.items(), key=lambda x: x[1], reverse=True)
        if len(sorted_cats) > 5:
            top_cats = sorted_cats[:4]
            others_stock = sum(x[1] for x in sorted_cats[4:])
            top_cats.append(('Others', others_stock))
        else:
            top_cats = sorted_cats
            
        labels = [x[0] for x in top_cats]
        values = [x[1] for x in top_cats]
        
        if not labels:
            return
            
        is_donut = self.chart_type_combo.currentIndex() == 1
        
        if is_donut:
            colors = ['#89B4FA', '#CBA6F7', '#F38BA8', '#A6E3A1', '#6C7086'] # Grey for Others
            # Move numbers outside the donut ring for perfect clarity on dark mode
            wedges, texts, autotexts = ax.pie(values, labels=None, autopct='%1.1f%%', 
                                          textprops={'color': '#CDD6F4', 'fontsize': 11, 'weight': 'bold'}, 
                                          wedgeprops={'width': 0.3, 'edgecolor': '#1E1E2E', 'linewidth': 3},
                                          colors=colors[:len(labels)], pctdistance=1.2)
            
            # Use Legend instead of crowded text labels
            legend = ax.legend(wedges, labels, title="Categories", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1), frameon=False)
            legend.get_title().set_color('#CDD6F4')
            for text in legend.get_texts():
                text.set_color('#CDD6F4')
                
            ax.set_title('Stock Distribution by Category', color='#CDD6F4', pad=25, fontsize=14, weight='bold')
        else:
            ax.bar(labels, values, color='#CBA6F7', edgecolor='#1E1E2E', linewidth=1)
            ax.set_title('Stock Available by Category', color='#CDD6F4', pad=25, fontsize=14, weight='bold')
            ax.set_ylabel('Total Stock', color='#CDD6F4', labelpad=15)
        
        # Adjust right margin heavily if donut to fit the legend
        r_margin = 0.65 if is_donut else 0.95
        fig.subplots_adjust(left=0.1, right=r_margin, top=0.85, bottom=0.15)
        fig.tight_layout(pad=3.0)
        canvas = FigureCanvas(fig)
        self.canvas_container.addWidget(canvas)
