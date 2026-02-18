"""
Smart Inventory & Expiry Management System
FILE: gui/app.py
PURPOSE: Main tkinter application window with tabbed navigation.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from gui.dashboard_tab import DashboardTab
from gui.inventory_tab import InventoryTab
from gui.sales_tab import SalesTab
from gui.expiry_tab import ExpiryTab
from gui.reports_tab import ReportsTab
from modules.expiry_monitor import run_expiry_check
from modules.scheduler import start_scheduler


# ─────────────────────────────────────────────────────────────
# Colour palette (dark professional theme)
# ─────────────────────────────────────────────────────────────
COLORS = {
    'bg':          '#1e1e2e',
    'sidebar':     '#181825',
    'card':        '#313244',
    'accent':      '#89b4fa',
    'accent2':     '#a6e3a1',
    'warning':     '#f9e2af',
    'danger':      '#f38ba8',
    'text':        '#cdd6f4',
    'text_dim':    '#6c7086',
    'white':       '#ffffff',
    'border':      '#45475a',
}

FONT_TITLE  = ('Segoe UI', 18, 'bold')
FONT_HEADER = ('Segoe UI', 12, 'bold')
FONT_BODY   = ('Segoe UI', 10)
FONT_SMALL  = ('Segoe UI', 9)


class SmartInventoryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart Inventory & Expiry Management System")
        self.geometry("1280x780")
        self.minsize(1100, 680)
        self.configure(bg=COLORS['bg'])
        self.resizable(True, True)

        self._apply_styles()
        self._build_layout()
        self._start_background_scheduler()

    # ── Styles ────────────────────────────────────────────────
    def _apply_styles(self):
        style = ttk.Style(self)
        style.theme_use('clam')

        style.configure('TNotebook',
                        background=COLORS['bg'],
                        borderwidth=0)
        style.configure('TNotebook.Tab',
                        background=COLORS['sidebar'],
                        foreground=COLORS['text_dim'],
                        padding=[16, 8],
                        font=FONT_BODY,
                        borderwidth=0)
        style.map('TNotebook.Tab',
                  background=[('selected', COLORS['card'])],
                  foreground=[('selected', COLORS['accent'])])

        style.configure('TFrame',  background=COLORS['bg'])
        style.configure('Card.TFrame', background=COLORS['card'])

        style.configure('TLabel',
                        background=COLORS['bg'],
                        foreground=COLORS['text'],
                        font=FONT_BODY)
        style.configure('Title.TLabel',
                        background=COLORS['bg'],
                        foreground=COLORS['accent'],
                        font=FONT_TITLE)
        style.configure('Header.TLabel',
                        background=COLORS['card'],
                        foreground=COLORS['text'],
                        font=FONT_HEADER)
        style.configure('Card.TLabel',
                        background=COLORS['card'],
                        foreground=COLORS['text'],
                        font=FONT_BODY)
        style.configure('Dim.TLabel',
                        background=COLORS['bg'],
                        foreground=COLORS['text_dim'],
                        font=FONT_SMALL)

        style.configure('Accent.TButton',
                        background=COLORS['accent'],
                        foreground=COLORS['bg'],
                        font=('Segoe UI', 10, 'bold'),
                        borderwidth=0,
                        relief='flat',
                        padding=[12, 6])
        style.map('Accent.TButton',
                  background=[('active', '#74c7ec')])

        style.configure('Danger.TButton',
                        background=COLORS['danger'],
                        foreground=COLORS['bg'],
                        font=('Segoe UI', 10, 'bold'),
                        borderwidth=0,
                        relief='flat',
                        padding=[12, 6])
        style.map('Danger.TButton',
                  background=[('active', '#eba0ac')])

        style.configure('TEntry',
                        fieldbackground=COLORS['card'],
                        foreground=COLORS['text'],
                        insertcolor=COLORS['text'],
                        bordercolor=COLORS['border'],
                        font=FONT_BODY)

        style.configure('TCombobox',
                        fieldbackground=COLORS['card'],
                        foreground=COLORS['text'],
                        background=COLORS['card'],
                        selectbackground=COLORS['accent'],
                        font=FONT_BODY)
        style.map('TCombobox',
                  fieldbackground=[('readonly', COLORS['card'])],
                  foreground=[('readonly', COLORS['text'])])

        # Treeview (tables)
        style.configure('Treeview',
                        background=COLORS['card'],
                        foreground=COLORS['text'],
                        fieldbackground=COLORS['card'],
                        rowheight=28,
                        font=FONT_BODY,
                        borderwidth=0)
        style.configure('Treeview.Heading',
                        background=COLORS['sidebar'],
                        foreground=COLORS['accent'],
                        font=('Segoe UI', 10, 'bold'),
                        relief='flat')
        style.map('Treeview',
                  background=[('selected', COLORS['accent'])],
                  foreground=[('selected', COLORS['bg'])])

        style.configure('TScrollbar',
                        background=COLORS['sidebar'],
                        troughcolor=COLORS['bg'],
                        borderwidth=0)

    # ── Layout ────────────────────────────────────────────────
    def _build_layout(self):
        # Top title bar
        title_bar = tk.Frame(self, bg=COLORS['sidebar'], height=56)
        title_bar.pack(fill='x', side='top')
        title_bar.pack_propagate(False)

        tk.Label(title_bar,
                 text="📦  Smart Inventory & Expiry Management",
                 bg=COLORS['sidebar'],
                 fg=COLORS['accent'],
                 font=FONT_TITLE).pack(side='left', padx=20, pady=10)

        tk.Label(title_bar,
                 text="Python + MySQL",
                 bg=COLORS['sidebar'],
                 fg=COLORS['text_dim'],
                 font=FONT_SMALL).pack(side='right', padx=20)

        # Notebook (tabs)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=0, pady=0)

        self.tab_dashboard = DashboardTab(self.notebook, COLORS)
        self.tab_inventory = InventoryTab(self.notebook, COLORS)
        self.tab_sales     = SalesTab(self.notebook, COLORS)
        self.tab_expiry    = ExpiryTab(self.notebook, COLORS)
        self.tab_reports   = ReportsTab(self.notebook, COLORS)

        self.notebook.add(self.tab_dashboard, text='  🏠  Dashboard  ')
        self.notebook.add(self.tab_inventory, text='  📦  Inventory  ')
        self.notebook.add(self.tab_sales,     text='  🛒  Sales  ')
        self.notebook.add(self.tab_expiry,    text='  ⚠️  Expiry  ')
        self.notebook.add(self.tab_reports,   text='  📊  Reports  ')

        # Refresh dashboard when switching tabs
        self.notebook.bind('<<NotebookTabChanged>>', self._on_tab_change)

    def _on_tab_change(self, event):
        tab = self.notebook.index(self.notebook.select())
        if tab == 0:
            self.tab_dashboard.refresh()

    # ── Background scheduler ──────────────────────────────────
    def _start_background_scheduler(self):
        def on_alert(count):
            # Show a popup alert on the main thread
            self.after(0, lambda: messagebox.showwarning(
                "Expiry Alert",
                f"⚠️  {count} batch(es) have expired and been logged.\n"
                "Check the Expiry tab for details."
            ))
        start_scheduler(run_expiry_check, on_alert_fn=on_alert)
