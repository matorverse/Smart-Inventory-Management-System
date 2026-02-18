"""
Smart Inventory & Expiry Management System
FILE: gui/dashboard_tab.py
PURPOSE: Home dashboard — KPI cards and quick overview.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from modules.reports import get_dashboard_kpis
from modules.expiry_monitor import run_expiry_check, get_expiring_soon


class DashboardTab(ttk.Frame):
    def __init__(self, parent, colors):
        super().__init__(parent)
        self.colors = colors
        self.configure(style='TFrame')
        self._build()
        self.refresh()

    def _build(self):
        C = self.colors

        # ── Page title ────────────────────────────────────────
        header = tk.Frame(self, bg=C['bg'], pady=16)
        header.pack(fill='x', padx=24)
        tk.Label(header, text="Dashboard", bg=C['bg'], fg=C['accent'],
                 font=('Segoe UI', 16, 'bold')).pack(side='left')
        ttk.Button(header, text="🔄  Refresh", style='Accent.TButton',
                   command=self.refresh).pack(side='right')
        ttk.Button(header, text="⚠️  Run Expiry Check", style='Danger.TButton',
                   command=self._manual_expiry_check).pack(side='right', padx=(0, 8))

        # ── KPI cards row ─────────────────────────────────────
        self.kpi_frame = tk.Frame(self, bg=C['bg'])
        self.kpi_frame.pack(fill='x', padx=24, pady=(0, 16))

        self.kpi_vars = {}
        kpi_defs = [
            ('total_products',  '📦 Products',       C['accent']),
            ('total_suppliers', '🏭 Suppliers',       C['accent2']),
            ('total_stock',     '📊 Total Stock',     C['accent']),
            ('low_stock_count', '🔴 Low Stock',       C['danger']),
            ('expiring_soon',   '⚠️ Expiring (7d)',   C['warning']),
            ('today_revenue',   '💰 Today Revenue',   C['accent2']),
        ]
        for i, (key, label, color) in enumerate(kpi_defs):
            card = tk.Frame(self.kpi_frame, bg=C['card'],
                            padx=20, pady=16, relief='flat')
            card.grid(row=0, column=i, padx=6, pady=4, sticky='nsew')
            self.kpi_frame.columnconfigure(i, weight=1)

            tk.Label(card, text=label, bg=C['card'],
                     fg=C['text_dim'], font=('Segoe UI', 9)).pack(anchor='w')
            var = tk.StringVar(value='—')
            self.kpi_vars[key] = var
            tk.Label(card, textvariable=var, bg=C['card'],
                     fg=color, font=('Segoe UI', 22, 'bold')).pack(anchor='w', pady=(4, 0))

        # ── Expiring soon table ───────────────────────────────
        tk.Label(self, text="⚠️  Expiring Within 7 Days",
                 bg=self.colors['bg'], fg=self.colors['warning'],
                 font=('Segoe UI', 12, 'bold')).pack(anchor='w', padx=24, pady=(8, 4))

        table_frame = tk.Frame(self, bg=C['bg'])
        table_frame.pack(fill='both', expand=True, padx=24, pady=(0, 16))

        cols = ('Batch ID', 'Product', 'Category', 'Supplier',
                'Expiry Date', 'Days Left', 'Qty Available')
        self.expiry_tree = ttk.Treeview(table_frame, columns=cols,
                                        show='headings', height=10)
        widths = [70, 180, 120, 160, 110, 80, 110]
        for col, w in zip(cols, widths):
            self.expiry_tree.heading(col, text=col)
            self.expiry_tree.column(col, width=w, anchor='center')

        vsb = ttk.Scrollbar(table_frame, orient='vertical',
                            command=self.expiry_tree.yview)
        self.expiry_tree.configure(yscrollcommand=vsb.set)
        self.expiry_tree.pack(side='left', fill='both', expand=True)
        vsb.pack(side='right', fill='y')

        # Tag colours for urgency
        self.expiry_tree.tag_configure('urgent',  background='#3b1e2e', foreground=C['danger'])
        self.expiry_tree.tag_configure('warning', background='#3b3120', foreground=C['warning'])
        self.expiry_tree.tag_configure('ok',      background=C['card'],  foreground=C['text'])

    def refresh(self):
        """Reload KPI values and expiring-soon table."""
        try:
            kpis = get_dashboard_kpis()
            if kpis:
                self.kpi_vars['total_products'].set(str(kpis.get('total_products', 0)))
                self.kpi_vars['total_suppliers'].set(str(kpis.get('total_suppliers', 0)))
                self.kpi_vars['total_stock'].set(str(kpis.get('total_stock', 0)))
                self.kpi_vars['low_stock_count'].set(str(kpis.get('low_stock_count', 0) or 0))
                self.kpi_vars['expiring_soon'].set(str(kpis.get('expiring_soon', 0)))
                rev = kpis.get('today_revenue', 0) or 0
                self.kpi_vars['today_revenue'].set(f"₹{rev:,.2f}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not load KPIs:\n{e}")

        # Expiring soon table
        for row in self.expiry_tree.get_children():
            self.expiry_tree.delete(row)
        try:
            rows = get_expiring_soon(7)
            for r in rows:
                days = r['days_left']
                tag = 'urgent' if days <= 2 else ('warning' if days <= 5 else 'ok')
                self.expiry_tree.insert('', 'end', values=(
                    r['batch_id'], r['product_name'], r['category_name'],
                    r['supplier_name'], str(r['expiry_date']),
                    f"{days} day(s)", r['quantity_available']
                ), tags=(tag,))
        except Exception as e:
            messagebox.showerror("Error", f"Could not load expiry data:\n{e}")

    def _manual_expiry_check(self):
        try:
            count = run_expiry_check()
            messagebox.showinfo("Expiry Check Complete",
                                f"✅  Expiry check done.\n{count} batch(es) logged to expiry log.")
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error", f"Expiry check failed:\n{e}")
