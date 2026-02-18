"""
Smart Inventory & Expiry Management System
FILE: gui/expiry_tab.py
PURPOSE: Expiry alerts (expiring soon) and full expiry audit log.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from modules.expiry_monitor import (
    run_expiry_check, get_expiring_soon, get_expiry_log, get_expiry_summary
)


class ExpiryTab(ttk.Frame):
    def __init__(self, parent, colors):
        super().__init__(parent)
        self.colors = colors
        self.configure(style='TFrame')
        self._build()
        self.refresh()

    def _build(self):
        C = self.colors

        # ── Header ────────────────────────────────────────────
        header = tk.Frame(self, bg=C['bg'], pady=12)
        header.pack(fill='x', padx=24)
        tk.Label(header, text="Expiry Monitoring", bg=C['bg'], fg=C['accent'],
                 font=('Segoe UI', 16, 'bold')).pack(side='left')
        ttk.Button(header, text="🔄 Refresh",
                   style='Accent.TButton', command=self.refresh).pack(side='right')
        ttk.Button(header, text="⚠️  Run Expiry Check",
                   style='Danger.TButton', command=self._run_check).pack(side='right', padx=(0, 8))

        # ── Summary cards ─────────────────────────────────────
        cards_frame = tk.Frame(self, bg=C['bg'])
        cards_frame.pack(fill='x', padx=24, pady=(0, 12))

        self.soon_var    = tk.StringVar(value='—')
        self.expired_var = tk.StringVar(value='—')

        for i, (var, label, color) in enumerate([
            (self.soon_var,    '⚠️  Expiring in 7 Days', C['warning']),
            (self.expired_var, '🔴  Expired with Stock',  C['danger']),
        ]):
            card = tk.Frame(cards_frame, bg=C['card'], padx=24, pady=14)
            card.grid(row=0, column=i, padx=6, sticky='nsew')
            cards_frame.columnconfigure(i, weight=1)
            tk.Label(card, text=label, bg=C['card'],
                     fg=C['text_dim'], font=('Segoe UI', 9)).pack(anchor='w')
            tk.Label(card, textvariable=var, bg=C['card'],
                     fg=color, font=('Segoe UI', 22, 'bold')).pack(anchor='w', pady=(4, 0))

        # ── Days filter ───────────────────────────────────────
        filter_frame = tk.Frame(self, bg=C['bg'])
        filter_frame.pack(fill='x', padx=24, pady=(0, 4))
        tk.Label(filter_frame, text="Show batches expiring within",
                 bg=C['bg'], fg=C['text_dim'], font=('Segoe UI', 9)).pack(side='left')
        self.days_var = tk.StringVar(value='7')
        days_entry = ttk.Entry(filter_frame, textvariable=self.days_var,
                               font=('Segoe UI', 10), width=4)
        days_entry.pack(side='left', padx=6)
        tk.Label(filter_frame, text="days", bg=C['bg'],
                 fg=C['text_dim'], font=('Segoe UI', 9)).pack(side='left')
        ttk.Button(filter_frame, text="Filter", style='Accent.TButton',
                   command=self._load_expiring).pack(side='left', padx=8)

        # ── Expiring soon table ───────────────────────────────
        tk.Label(self, text="Batches Expiring Soon",
                 bg=C['bg'], fg=C['warning'],
                 font=('Segoe UI', 12, 'bold')).pack(anchor='w', padx=24, pady=(4, 2))

        soon_frame = tk.Frame(self, bg=C['bg'])
        soon_frame.pack(fill='both', expand=True, padx=24, pady=(0, 8))

        cols = ('Batch ID', 'Product', 'Category', 'Supplier',
                'Expiry Date', 'Days Left', 'Qty Available')
        self.soon_tree = ttk.Treeview(soon_frame, columns=cols,
                                      show='headings', height=7)
        widths = [70, 180, 120, 160, 110, 80, 110]
        for col, w in zip(cols, widths):
            self.soon_tree.heading(col, text=col)
            self.soon_tree.column(col, width=w, anchor='center')
        vsb = ttk.Scrollbar(soon_frame, orient='vertical', command=self.soon_tree.yview)
        self.soon_tree.configure(yscrollcommand=vsb.set)
        self.soon_tree.pack(side='left', fill='both', expand=True)
        vsb.pack(side='right', fill='y')

        self.soon_tree.tag_configure('urgent',  background='#3b1e2e', foreground=C['danger'])
        self.soon_tree.tag_configure('warning', background='#3b3120', foreground=C['warning'])
        self.soon_tree.tag_configure('ok',      background=C['card'],  foreground=C['text'])

        # ── Expiry log table ──────────────────────────────────
        tk.Label(self, text="Expiry Audit Log (Waste Record)",
                 bg=C['bg'], fg=C['danger'],
                 font=('Segoe UI', 12, 'bold')).pack(anchor='w', padx=24, pady=(4, 2))

        log_frame = tk.Frame(self, bg=C['bg'])
        log_frame.pack(fill='both', expand=True, padx=24, pady=(0, 16))

        log_cols = ('Expiry ID', 'Batch ID', 'Product', 'Category',
                    'Qty Expired', 'Expiry Date', 'Logged On', 'Waste Value (₹)')
        self.log_tree = ttk.Treeview(log_frame, columns=log_cols,
                                     show='headings', height=7)
        log_widths = [70, 70, 160, 110, 100, 110, 160, 120]
        for col, w in zip(log_cols, log_widths):
            self.log_tree.heading(col, text=col)
            self.log_tree.column(col, width=w, anchor='center')
        vsb2 = ttk.Scrollbar(log_frame, orient='vertical', command=self.log_tree.yview)
        self.log_tree.configure(yscrollcommand=vsb2.set)
        self.log_tree.pack(side='left', fill='both', expand=True)
        vsb2.pack(side='right', fill='y')

    def refresh(self):
        self._load_summary()
        self._load_expiring()
        self._load_log()

    def _load_summary(self):
        try:
            s = get_expiry_summary()
            if s:
                self.soon_var.set(str(s.get('expiring_soon', 0) or 0))
                self.expired_var.set(str(s.get('expired_with_stock', 0) or 0))
        except Exception as e:
            messagebox.showerror("Error", f"Could not load summary:\n{e}")

    def _load_expiring(self):
        for row in self.soon_tree.get_children():
            self.soon_tree.delete(row)
        try:
            days = int(self.days_var.get() or 7)
            rows = get_expiring_soon(days)
            for r in rows:
                d = r['days_left']
                tag = 'urgent' if d <= 2 else ('warning' if d <= 5 else 'ok')
                self.soon_tree.insert('', 'end', values=(
                    r['batch_id'], r['product_name'], r['category_name'],
                    r['supplier_name'], str(r['expiry_date']),
                    f"{d} day(s)", r['quantity_available']
                ), tags=(tag,))
        except Exception as e:
            messagebox.showerror("Error", f"Could not load expiring batches:\n{e}")

    def _load_log(self):
        for row in self.log_tree.get_children():
            self.log_tree.delete(row)
        try:
            rows = get_expiry_log()
            for r in rows:
                self.log_tree.insert('', 'end', values=(
                    r['expiry_id'], r['batch_id'], r['product_name'],
                    r['category_name'], r['quantity_expired'],
                    str(r['expiry_date']), str(r['logged_on']),
                    f"₹{r['waste_value']}"
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Could not load expiry log:\n{e}")

    def _run_check(self):
        try:
            count = run_expiry_check()
            messagebox.showinfo("Done",
                f"✅  Expiry check complete.\n{count} batch(es) logged.")
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e))
