"""
Toast Notification Widget
Displays temporary notification messages in the UI
"""

import logging
from typing import Literal

import customtkinter as ctk

logger = logging.getLogger("LinuxArmoury")


class ToastNotification(ctk.CTkFrame):
    """
    A toast notification widget that appears temporarily in the UI
    """

    # Color schemes for different notification types
    COLORS = {
        "success": ("#10b981", "#ffffff", "✓"),  # green
        "error": ("#ef4444", "#ffffff", "✗"),  # red
        "info": ("#3b82f6", "#ffffff", "ℹ"),  # blue
        "warning": ("#f59e0b", "#ffffff", "⚠"),  # orange
    }

    def __init__(
        self,
        master,
        message: str,
        type: Literal["success", "error", "info", "warning"] = "info",
        duration: int = 5000,
    ):
        """
        Initialize toast notification

        Args:
            master: Parent widget
            message: Message to display
            type: Notification type (success, error, info, warning)
            duration: How long to display in milliseconds
        """
        super().__init__(master, corner_radius=8)

        self.message = message
        self.type = type
        self.duration = duration
        self.is_visible = False

        # Get colors for this type
        bg_color, text_color, icon = self.COLORS.get(type, self.COLORS["info"])
        self.configure(fg_color=bg_color)

        # Create container frame
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=2, pady=2)

        # Icon
        icon_label = ctk.CTkLabel(
            container,
            text=icon,
            font=("Arial", 20, "bold"),
            text_color=text_color,
            width=30,
        )
        icon_label.pack(side="left", padx=(10, 5))

        # Message
        msg_label = ctk.CTkLabel(
            container,
            text=message,
            font=("Arial", 12),
            text_color=text_color,
            wraplength=300,
        )
        msg_label.pack(side="left", padx=(5, 10), pady=10)

        # Close button
        close_btn = ctk.CTkButton(
            container,
            text="×",
            width=20,
            height=20,
            font=("Arial", 16, "bold"),
            fg_color="transparent",
            hover_color=bg_color,
            text_color=text_color,
            command=self.dismiss,
        )
        close_btn.pack(side="right", padx=(0, 5))

        logger.debug(f"Toast created: {type} - {message}")

    def show(self):
        """Display the toast notification"""
        if self.is_visible:
            return

        self.is_visible = True

        # Position at top-right of window
        self.place(relx=0.98, rely=0.02, anchor="ne")

        # Fade in animation
        self._fade_in(0.0)

        # Auto-dismiss after duration
        self.after(self.duration, self.dismiss)

    def _fade_in(self, alpha: float = 0.0):
        """Fade in animation"""
        if not self.is_visible or not self.winfo_exists():
            return

        alpha = min(alpha + 0.1, 1.0)
        try:
            self.attributes("-alpha", alpha)
        except Exception:
            # Alpha not supported on all platforms
            pass

        if alpha < 1.0:
            self.after(30, lambda: self._fade_in(alpha))

    def dismiss(self):
        """Dismiss the toast notification"""
        if not self.is_visible:
            return

        self.is_visible = False
        self._fade_out(1.0)

    def _fade_out(self, alpha: float = 1.0):
        """Fade out animation"""
        if not self.winfo_exists():
            return

        alpha = max(alpha - 0.1, 0.0)
        try:
            self.attributes("-alpha", alpha)
        except Exception:
            pass

        if alpha > 0:
            self.after(30, lambda: self._fade_out(alpha))
        else:
            try:
                self.destroy()
            except Exception:
                pass


class ToastManager:
    """
    Manages multiple toast notifications
    Stacks them vertically and handles positioning
    """

    def __init__(self, master):
        self.master = master
        self.toasts = []
        self.max_toasts = 5

    def show(
        self,
        message: str,
        type: Literal["success", "error", "info", "warning"] = "info",
        duration: int = 5000,
    ):
        """
        Show a new toast notification

        Args:
            message: Message to display
            type: Notification type
            duration: Display duration in milliseconds
        """
        # Remove old toasts if we have too many
        if len(self.toasts) >= self.max_toasts:
            oldest = self.toasts.pop(0)
            oldest.dismiss()

        # Create new toast
        toast = ToastNotification(self.master, message, type, duration)
        self.toasts.append(toast)

        # Position toast (stack vertically)
        self._reposition_toasts()

        # Show toast
        toast.show()

        # Remove from list when dismissed
        def on_destroy():
            if toast in self.toasts:
                self.toasts.remove(toast)
                self._reposition_toasts()

        # Check for destruction
        def check_exists():
            if not toast.winfo_exists():
                on_destroy()
            elif toast.is_visible:
                toast.after(100, check_exists)

        toast.after(100, check_exists)

    def _reposition_toasts(self):
        """Reposition all visible toasts"""
        y_offset = 0.02
        for toast in self.toasts:
            if toast.winfo_exists() and toast.is_visible:
                toast.place(relx=0.98, rely=y_offset, anchor="ne")
                y_offset += 0.08  # Stack with spacing
