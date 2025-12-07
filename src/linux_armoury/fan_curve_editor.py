#!/usr/bin/env python3
"""
Visual Fan Curve Editor for Linux Armoury
Allows users to create custom fan curves by dragging points on a graph.
"""

import math
from dataclasses import dataclass
from typing import Callable, List, Optional, Tuple

import cairo
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gdk, Gtk  # noqa: E402


@dataclass
class FanCurvePoint:
    """A point on the fan curve"""

    temperature: int  # Temperature in Celsius (0-100)
    fan_speed: int  # Fan speed percentage (0-100)

    def __post_init__(self):
        self.temperature = max(0, min(100, self.temperature))
        self.fan_speed = max(0, min(100, self.fan_speed))


class FanCurveWidget(Gtk.DrawingArea):
    """Interactive widget for editing fan curves visually"""

    def __init__(self, on_curve_changed: Optional[Callable] = None):
        super().__init__()

        # Default fan curve points (temperature, fan_speed)
        self.points: List[FanCurvePoint] = [
            FanCurvePoint(30, 0),
            FanCurvePoint(50, 30),
            FanCurvePoint(70, 60),
            FanCurvePoint(85, 100),
        ]

        self.on_curve_changed = on_curve_changed
        self.selected_point: Optional[int] = None
        self.hovered_point: Optional[int] = None
        self.dragging = False

        # Styling
        self.padding = 40
        self.point_radius = 8
        self.point_hover_radius = 10

        # Colors (RGBA tuples)
        self.bg_color = (0.15, 0.15, 0.18, 1.0)
        self.grid_color = (0.3, 0.3, 0.35, 0.5)
        self.curve_color = (0.35, 0.65, 0.95, 1.0)
        self.curve_fill_color = (0.35, 0.65, 0.95, 0.2)
        self.point_color = (0.95, 0.65, 0.35, 1.0)
        self.point_selected_color = (0.95, 0.35, 0.35, 1.0)
        self.text_color = (0.8, 0.8, 0.8, 1.0)

        # Temperature zones (for visual hints)
        self.temp_zones = [
            (0, 50, (0.2, 0.6, 0.3, 0.1)),  # Cool (green tint)
            (50, 70, (0.6, 0.6, 0.2, 0.1)),  # Warm (yellow tint)
            (70, 85, (0.7, 0.4, 0.2, 0.1)),  # Hot (orange tint)
            (85, 100, (0.7, 0.2, 0.2, 0.1)),  # Critical (red tint)
        ]

        # Set minimum size
        self.set_size_request(400, 280)
        self.set_hexpand(True)
        self.set_vexpand(True)

        # Set up drawing
        self.set_draw_func(self.on_draw)

        # Set up event controllers
        self.setup_event_controllers()

    def setup_event_controllers(self):
        """Set up mouse event handlers"""
        # Motion controller for hover effects
        motion = Gtk.EventControllerMotion.new()
        motion.connect("motion", self.on_motion)
        motion.connect("leave", self.on_leave)
        self.add_controller(motion)

        # Click controller for selecting/dragging points
        click = Gtk.GestureClick.new()
        click.connect("pressed", self.on_press)
        click.connect("released", self.on_release)
        self.add_controller(click)

        # Drag controller
        drag = Gtk.GestureDrag.new()
        drag.connect("drag-begin", self.on_drag_begin)
        drag.connect("drag-update", self.on_drag_update)
        drag.connect("drag-end", self.on_drag_end)
        self.add_controller(drag)

    def coords_to_point(self, x: float, y: float) -> Tuple[int, int]:
        """Convert widget coordinates to temperature/speed values"""
        width = self.get_width()
        height = self.get_height()

        graph_width = width - 2 * self.padding
        graph_height = height - 2 * self.padding

        temp = int((x - self.padding) / graph_width * 100)
        speed = int((1 - (y - self.padding) / graph_height) * 100)

        return (max(0, min(100, temp)), max(0, min(100, speed)))

    def point_to_coords(self, temp: int, speed: int) -> Tuple[float, float]:
        """Convert temperature/speed values to widget coordinates"""
        width = self.get_width()
        height = self.get_height()

        graph_width = width - 2 * self.padding
        graph_height = height - 2 * self.padding

        x = self.padding + (temp / 100) * graph_width
        y = self.padding + (1 - speed / 100) * graph_height

        return (x, y)

    def find_point_at(self, x: float, y: float) -> Optional[int]:
        """Find if there is a curve point at the given coordinates"""
        for i, point in enumerate(self.points):
            px, py = self.point_to_coords(point.temperature, point.fan_speed)
            dist = math.sqrt((x - px) ** 2 + (y - py) ** 2)
            if dist <= self.point_hover_radius:
                return i
        return None

    def on_motion(self, controller, x, y):
        """Handle mouse motion for hover effects"""
        self.hovered_point = self.find_point_at(x, y)
        self.queue_draw()

    def on_leave(self, controller):
        """Handle mouse leaving the widget"""
        self.hovered_point = None
        self.queue_draw()

    def on_press(self, gesture, n_press, x, y):
        """Handle mouse press"""
        point_idx = self.find_point_at(x, y)

        if point_idx is not None:
            self.selected_point = point_idx
            self.dragging = True
        elif n_press == 2:
            # Double-click to add new point
            temp, speed = self.coords_to_point(x, y)
            self.add_point(temp, speed)

        self.queue_draw()

    def on_release(self, gesture, n_press, x, y):
        """Handle mouse release"""
        self.dragging = False
        self.queue_draw()

    def on_drag_begin(self, gesture, start_x, start_y):
        """Handle drag start"""
        self.selected_point = self.find_point_at(start_x, start_y)
        if self.selected_point is not None:
            self.dragging = True

    def on_drag_update(self, gesture, offset_x, offset_y):
        """Handle drag motion"""
        if not self.dragging or self.selected_point is None:
            return

        success, start_x, start_y = gesture.get_start_point()
        if not success:
            return

        x = start_x + offset_x
        y = start_y + offset_y

        temp, speed = self.coords_to_point(x, y)

        # Update point
        self.points[self.selected_point] = FanCurvePoint(temp, speed)

        # Sort points by temperature
        self.points.sort(key=lambda p: p.temperature)

        # Find new index of selected point
        for i, p in enumerate(self.points):
            if p.temperature == temp and p.fan_speed == speed:
                self.selected_point = i
                break

        self.queue_draw()

    def on_drag_end(self, gesture, offset_x, offset_y):
        """Handle drag end"""
        self.dragging = False
        if self.on_curve_changed:
            self.on_curve_changed(self.get_curve_data())
        self.queue_draw()

    def add_point(self, temp: int, speed: int):
        """Add a new point to the curve"""
        new_point = FanCurvePoint(temp, speed)
        self.points.append(new_point)
        self.points.sort(key=lambda p: p.temperature)

        if self.on_curve_changed:
            self.on_curve_changed(self.get_curve_data())

        self.queue_draw()

    def remove_selected_point(self):
        """Remove the currently selected point"""
        if self.selected_point is not None and len(self.points) > 2:
            del self.points[self.selected_point]
            self.selected_point = None

            if self.on_curve_changed:
                self.on_curve_changed(self.get_curve_data())

            self.queue_draw()

    def get_curve_data(self) -> List[Tuple[int, int]]:
        """Get the curve as a list of (temperature, fan_speed) tuples"""
        return [(p.temperature, p.fan_speed) for p in self.points]

    def set_curve_data(self, data: List[Tuple[int, int]]):
        """Set the curve from a list of (temperature, fan_speed) tuples"""
        self.points = [FanCurvePoint(t, s) for t, s in data]
        self.points.sort(key=lambda p: p.temperature)
        self.queue_draw()

    def on_draw(self, area, cr, width, height):
        """Draw the fan curve editor"""
        # Background
        cr.set_source_rgba(*self.bg_color)
        cr.paint()

        graph_left = self.padding
        graph_right = width - self.padding
        graph_top = self.padding
        graph_bottom = height - self.padding
        graph_width = graph_right - graph_left
        graph_height = graph_bottom - graph_top

        # Draw temperature zones
        for start_temp, end_temp, color in self.temp_zones:
            x1 = graph_left + (start_temp / 100) * graph_width
            x2 = graph_left + (end_temp / 100) * graph_width
            cr.set_source_rgba(*color)
            cr.rectangle(x1, graph_top, x2 - x1, graph_height)
            cr.fill()

        # Draw grid lines
        cr.set_source_rgba(*self.grid_color)
        cr.set_line_width(1)

        # Vertical grid lines (temperature)
        for temp in range(0, 101, 10):
            x = graph_left + (temp / 100) * graph_width
            cr.move_to(x, graph_top)
            cr.line_to(x, graph_bottom)
            cr.stroke()

        # Horizontal grid lines (fan speed)
        for speed in range(0, 101, 20):
            y = graph_top + (1 - speed / 100) * graph_height
            cr.move_to(graph_left, y)
            cr.line_to(graph_right, y)
            cr.stroke()

        # Draw axis labels
        cr.set_source_rgba(*self.text_color)
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        cr.set_font_size(10)

        # Temperature labels
        for temp in [0, 30, 50, 70, 85, 100]:
            x = graph_left + (temp / 100) * graph_width
            cr.move_to(x - 8, graph_bottom + 15)
            cr.show_text(f"{temp}°")

        # Speed labels
        for speed in [0, 50, 100]:
            y = graph_top + (1 - speed / 100) * graph_height
            cr.move_to(graph_left - 25, y + 4)
            cr.show_text(f"{speed}%")

        # Draw axis titles
        cr.set_font_size(12)
        cr.move_to(width / 2 - 40, height - 5)
        cr.show_text("Temperature (°C)")

        cr.save()
        cr.translate(12, height / 2 + 40)
        cr.rotate(-math.pi / 2)
        cr.show_text("Fan Speed (%)")
        cr.restore()

        # Draw curve fill
        if len(self.points) >= 2:
            cr.set_source_rgba(*self.curve_fill_color)
            cr.move_to(graph_left, graph_bottom)

            for point in self.points:
                x, y = self.point_to_coords(point.temperature, point.fan_speed)
                cr.line_to(x, y)

            cr.line_to(graph_right, graph_bottom)
            cr.close_path()
            cr.fill()

        # Draw curve line
        if len(self.points) >= 2:
            cr.set_source_rgba(*self.curve_color)
            cr.set_line_width(3)

            first = True
            for point in self.points:
                x, y = self.point_to_coords(point.temperature, point.fan_speed)
                if first:
                    cr.move_to(x, y)
                    first = False
                else:
                    cr.line_to(x, y)
            cr.stroke()

        # Draw points
        for i, point in enumerate(self.points):
            x, y = self.point_to_coords(point.temperature, point.fan_speed)

            # Determine point appearance
            if i == self.selected_point:
                color = self.point_selected_color
                radius = self.point_hover_radius
            elif i == self.hovered_point:
                color = self.point_color
                radius = self.point_hover_radius
            else:
                color = self.point_color
                radius = self.point_radius

            # Draw point shadow
            cr.set_source_rgba(0, 0, 0, 0.3)
            cr.arc(x + 2, y + 2, radius, 0, 2 * math.pi)
            cr.fill()

            # Draw point
            cr.set_source_rgba(*color)
            cr.arc(x, y, radius, 0, 2 * math.pi)
            cr.fill()

            # Draw point border
            cr.set_source_rgba(1, 1, 1, 0.8)
            cr.set_line_width(2)
            cr.arc(x, y, radius, 0, 2 * math.pi)
            cr.stroke()

        # Draw selected point info
        if self.selected_point is not None:
            point = self.points[self.selected_point]
            info_text = f"{point.temperature}°C → {point.fan_speed}%"

            cr.set_source_rgba(0, 0, 0, 0.7)
            cr.rectangle(graph_right - 90, graph_top, 85, 25)
            cr.fill()

            cr.set_source_rgba(1, 1, 1, 1)
            cr.set_font_size(12)
            cr.move_to(graph_right - 85, graph_top + 17)
            cr.show_text(info_text)


# Preset fan curves
PRESET_CURVES = {
    "silent": [(30, 0), (50, 20), (70, 40), (85, 60), (95, 80)],
    "balanced": [(30, 10), (50, 30), (70, 60), (85, 80), (95, 100)],
    "performance": [(30, 20), (50, 50), (70, 80), (85, 100)],
    "aggressive": [(30, 30), (50, 70), (70, 90), (85, 100)],
    "full_speed": [(30, 100), (100, 100)],
}


def get_preset_curve(preset_name: str) -> List[Tuple[int, int]]:
    """Get a preset fan curve by name"""
    return PRESET_CURVES.get(preset_name.lower(), PRESET_CURVES["balanced"])


class FanCurveEditorDialog(Adw.Dialog):
    """Dialog for editing fan curves"""

    def __init__(self, fan_name: str = "CPU Fan", on_apply: Optional[Callable] = None):
        super().__init__()

        self.fan_name = fan_name
        self.on_apply = on_apply

        self.set_title(f"Fan Curve Editor - {fan_name}")
        self.set_content_width(550)
        self.set_content_height(450)

        self.setup_ui()

    def setup_ui(self):
        """Set up the dialog UI"""
        # Main box
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        # Header bar
        header = Adw.HeaderBar()
        header.set_show_end_title_buttons(True)
        header.set_show_start_title_buttons(True)

        # Apply button
        apply_btn = Gtk.Button(label="Apply")
        apply_btn.add_css_class("suggested-action")
        apply_btn.connect("clicked", self.on_apply_clicked)
        header.pack_end(apply_btn)

        main_box.append(header)

        # Content
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        content_box.set_margin_top(12)
        content_box.set_margin_bottom(12)
        content_box.set_margin_start(12)
        content_box.set_margin_end(12)

        # Preset selector row
        preset_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        preset_label = Gtk.Label(label="Preset:")
        preset_label.add_css_class("dim-label")

        self.preset_dropdown = Gtk.DropDown.new_from_strings(
            ["Silent", "Balanced", "Performance", "Aggressive", "Full Speed", "Custom"]
        )
        self.preset_dropdown.set_selected(1)  # Default to Balanced
        self.preset_dropdown.connect("notify::selected", self.on_preset_changed)
        self.preset_dropdown.set_hexpand(True)

        preset_box.append(preset_label)
        preset_box.append(self.preset_dropdown)
        content_box.append(preset_box)

        # Fan curve widget
        self.curve_widget = FanCurveWidget(on_curve_changed=self.on_curve_changed)
        self.curve_widget.add_css_class("card")
        content_box.append(self.curve_widget)

        # Help text
        help_label = Gtk.Label(
            label="💡 Drag points to adjust. Double-click to add a point. Select and press Delete to remove."
        )
        help_label.add_css_class("dim-label")
        help_label.set_wrap(True)
        help_label.set_margin_top(6)
        content_box.append(help_label)

        # Button row
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        button_box.set_halign(Gtk.Align.END)
        button_box.set_margin_top(8)

        reset_btn = Gtk.Button(label="Reset to Default")
        reset_btn.connect("clicked", self.on_reset_clicked)
        button_box.append(reset_btn)

        remove_btn = Gtk.Button(label="Remove Point")
        remove_btn.add_css_class("destructive-action")
        remove_btn.connect("clicked", self.on_remove_clicked)
        button_box.append(remove_btn)

        content_box.append(button_box)

        main_box.append(content_box)
        self.set_child(main_box)

        # Set up keyboard handler for delete key
        key_controller = Gtk.EventControllerKey.new()
        key_controller.connect("key-pressed", self.on_key_pressed)
        self.curve_widget.add_controller(key_controller)

    def on_preset_changed(self, dropdown, param):
        """Handle preset selection change"""
        selected = dropdown.get_selected()
        presets = ["silent", "balanced", "performance", "aggressive", "full_speed"]

        if selected < len(presets):
            preset_name = presets[selected]
            curve_data = get_preset_curve(preset_name)
            self.curve_widget.set_curve_data(curve_data)

    def on_curve_changed(self, curve_data):
        """Handle curve change - set to Custom preset"""
        self.preset_dropdown.set_selected(5)  # Set to "Custom"

    def on_reset_clicked(self, button):
        """Reset to balanced preset"""
        self.preset_dropdown.set_selected(1)
        self.curve_widget.set_curve_data(get_preset_curve("balanced"))

    def on_remove_clicked(self, button):
        """Remove selected point"""
        self.curve_widget.remove_selected_point()

    def on_key_pressed(self, controller, keyval, keycode, state):
        """Handle key press events"""
        if keyval == Gdk.KEY_Delete or keyval == Gdk.KEY_BackSpace:
            self.curve_widget.remove_selected_point()
            return True
        return False

    def on_apply_clicked(self, button):
        """Apply the fan curve"""
        if self.on_apply:
            curve_data = self.curve_widget.get_curve_data()
            self.on_apply(self.fan_name, curve_data)
        self.close()

    def get_curve_data(self) -> List[Tuple[int, int]]:
        """Get the current curve data"""
        return self.curve_widget.get_curve_data()

    def set_curve_data(self, data: List[Tuple[int, int]]):
        """Set the curve data"""
        self.curve_widget.set_curve_data(data)
