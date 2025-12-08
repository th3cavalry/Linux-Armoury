"""
Real-Time Monitoring Graph Widget
Displays live system metrics with matplotlib
"""

import logging
from collections import deque

import customtkinter as ctk
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

logger = logging.getLogger("LinuxArmoury")


class LiveMonitoringGraph(ctk.CTkFrame):
    """
    A widget that displays a live graph of system metrics
    """

    def __init__(
        self,
        master,
        title: str,
        max_points: int = 60,
        color: str = "#ff0066",
        unit: str = "%",
        min_val: float = 0,
        max_val: float = 100,
    ):
        """
        Initialize live monitoring graph

        Args:
            master: Parent widget
            title: Graph title
            max_points: Maximum number of data points to display
            color: Line color
            unit: Unit of measurement
            min_val: Minimum Y-axis value
            max_val: Maximum Y-axis value
        """
        super().__init__(master, fg_color="#2a2a2a", corner_radius=8)

        self.title = title
        self.max_points = max_points
        self.color = color
        self.unit = unit
        self.min_val = min_val
        self.max_val = max_val

        # Data storage
        self.data = deque([0] * max_points, maxlen=max_points)

        # Title label
        title_label = ctk.CTkLabel(
            self, text=title, font=("Arial", 14, "bold"), text_color="#ffffff"
        )
        title_label.pack(pady=(10, 5))

        # Create matplotlib figure
        self.fig = Figure(figsize=(6, 2.5), facecolor="#2a2a2a", dpi=90)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor("#1a1a1a")

        # Style the plot
        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)
        self.ax.spines["left"].set_color("#444444")
        self.ax.spines["bottom"].set_color("#444444")
        self.ax.tick_params(colors="#888888", labelsize=8)
        self.ax.set_ylim(min_val, max_val)
        self.ax.set_xlim(0, max_points)
        self.ax.grid(True, alpha=0.2, color="#444444", linestyle="--")

        # Remove x-axis labels (time is implicit)
        self.ax.set_xticks([])

        # Y-axis label
        self.ax.set_ylabel(unit, color="#888888", fontsize=9)

        # Initial line
        (self.line,) = self.ax.plot([], [], color=color, linewidth=2, antialiased=True)

        # Fill area under line
        self.fill = None

        # Embed in CustomTkinter
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(0, 5))

        # Current value label
        self.value_label = ctk.CTkLabel(
            self, text=f"0{unit}", font=("Arial", 12, "bold"), text_color=color
        )
        self.value_label.pack(pady=(0, 10))

        # Statistics labels (min/avg/max)
        stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        stats_frame.pack(pady=(0, 5))

        self.min_label = ctk.CTkLabel(
            stats_frame, text=f"Min: 0{unit}", font=("Arial", 8), text_color="#888888"
        )
        self.min_label.pack(side="left", padx=5)

        self.avg_label = ctk.CTkLabel(
            stats_frame, text=f"Avg: 0{unit}", font=("Arial", 8), text_color="#888888"
        )
        self.avg_label.pack(side="left", padx=5)

        self.max_label = ctk.CTkLabel(
            stats_frame, text=f"Max: 0{unit}", font=("Arial", 8), text_color="#888888"
        )
        self.max_label.pack(side="left", padx=5)

        logger.debug(f"Monitoring graph created: {title}")

    def update_data(self, value: float):
        """
        Update graph with new data point

        Args:
            value: New value to add to graph
        """
        # Add new data point
        self.data.append(value)

        # Update line data
        x = np.arange(len(self.data))
        y = list(self.data)
        self.line.set_data(x, y)

        # Update fill
        if self.fill:
            self.fill.remove()
        self.fill = self.ax.fill_between(x, y, 0, alpha=0.3, color=self.color)

        # Update current value label
        self.value_label.configure(text=f"{value:.1f}{self.unit}")

        # Update statistics
        valid_data = [d for d in self.data if d > 0]
        if valid_data:
            min_val = min(valid_data)
            avg_val = sum(valid_data) / len(valid_data)
            max_val = max(valid_data)

            self.min_label.configure(text=f"Min: {min_val:.1f}{self.unit}")
            self.avg_label.configure(text=f"Avg: {avg_val:.1f}{self.unit}")
            self.max_label.configure(text=f"Max: {max_val:.1f}{self.unit}")

        # Redraw canvas
        try:
            self.canvas.draw_idle()
        except Exception as e:
            logger.debug(f"Graph draw error: {e}")

    def clear(self):
        """Clear all data from the graph"""
        self.data = deque([0] * self.max_points, maxlen=self.max_points)
        self.update_data(0)
        logger.debug(f"Graph cleared: {self.title}")

    def set_color(self, color: str):
        """Change the line color"""
        self.color = color
        self.line.set_color(color)
        self.value_label.configure(text_color=color)
        self.canvas.draw_idle()


class MultiGraphPanel(ctk.CTkFrame):
    """
    Panel containing multiple monitoring graphs
    """

    def __init__(self, master, graphs: list):
        """
        Initialize multi-graph panel

        Args:
            master: Parent widget
            graphs: List of graph configurations.
                Each item should be a dict with keys like "title" and "color".
        """
        super().__init__(master, fg_color="transparent")

        self.graphs = {}

        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        for i in range(len(graphs)):
            self.grid_columnconfigure(i, weight=1)

        # Create graphs
        for i, config in enumerate(graphs):
            graph = LiveMonitoringGraph(
                self,
                title=config.get("title", f"Graph {i+1}"),
                max_points=config.get("max_points", 60),
                color=config.get("color", "#ff0066"),
                unit=config.get("unit", "%"),
                min_val=config.get("min_val", 0),
                max_val=config.get("max_val", 100),
            )
            graph.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")

            # Store reference
            self.graphs[config.get("name", f"graph_{i}")] = graph

    def update(self, data: dict):
        """
        Update all graphs with new data

        Args:
            data: Dictionary of graph_name: value pairs
        """
        for name, value in data.items():
            if name in self.graphs:
                self.graphs[name].update_data(value)

    def get_graph(self, name: str) -> LiveMonitoringGraph:
        """Get a specific graph by name"""
        return self.graphs.get(name)
