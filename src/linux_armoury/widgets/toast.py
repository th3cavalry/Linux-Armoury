import threading
from typing import Literal

import customtkinter as ctk


class ToastNotification(ctk.CTkToplevel):
    """Toast notification widget for displaying temporary messages"""

    def __init__(
        self,
        master,
        message: str,
        notification_type: Literal["success", "error", "info", "warning"] = "info",
        duration: int = 3000,
    ):
        super().__init__(master)

        self.message = message
        self.notification_type = notification_type
        self.duration = duration  # milliseconds

        # Remove window decorations
        self.overrideredirect(True)
        self.attributes("-topmost", True)

        # Color scheme based on notification type
        colors = {
            "success": ("#10b981", "#065f46", "✓"),
            "error": ("#ef4444", "#991b1b", "✗"),
            "info": ("#3b82f6", "#1e3a8a", "ℹ"),
            "warning": ("#f59e0b", "#92400e", "⚠"),
        }

        bg_color, border_color, icon = colors[notification_type]
        self.bg_color = bg_color
        self.configure(fg_color=bg_color)

        # Main frame with padding
        main_frame = ctk.CTkFrame(self, fg_color=bg_color, corner_radius=8)
        main_frame.pack(padx=1, pady=1, fill="both", expand=True)

        # Content frame
        content_frame = ctk.CTkFrame(main_frame, fg_color=bg_color)
        content_frame.pack(padx=15, pady=12, fill="both", expand=True)

        # Icon and message in horizontal layout
        icon_label = ctk.CTkLabel(
            content_frame,
            text=icon,
            font=("Arial", 18, "bold"),
            text_color="white",
        )
        icon_label.pack(side="left", padx=(0, 10))

        msg_label = ctk.CTkLabel(
            content_frame,
            text=message,
            font=("Arial", 12),
            text_color="white",
            wraplength=300,
        )
        msg_label.pack(side="left", fill="both", expand=True)

        # Get screen dimensions
        self.update_idletasks()
        width = self.winfo_reqwidth()

        # Position at top-right corner
        screen_width = self.winfo_screenwidth()
        x = screen_width - width - 20
        y = 20

        self.geometry(f"+{x}+{y}")

        # Auto-dismiss after duration
        self.dismiss_timer = None
        self.schedule_dismiss()

    def schedule_dismiss(self):
        """Schedule the notification to dismiss after duration"""
        self.dismiss_timer = threading.Timer(self.duration / 1000, self.fade_out)
        self.dismiss_timer.daemon = True
        self.dismiss_timer.start()

    def fade_out(self):
        """Fade out and destroy the notification"""
        try:
            self.destroy()
        except Exception:
            pass

    def cancel_dismiss(self):
        """Cancel the auto-dismiss timer"""
        if self.dismiss_timer:
            self.dismiss_timer.cancel()
