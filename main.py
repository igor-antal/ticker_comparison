import tkinter as tk
from tkinter import OptionMenu, StringVar, messagebox
from tkinter import Tk, ttk
import matplotlib.pyplot as plt
from data_manager import DataManager
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


class App(Tk):
    def __init__(self):
        super().__init__()
        self._dm = DataManager()

        self.geometry("900x600")
        self.title("Ticker Comparison Tool")

        self._main_frame = ttk.Frame(self)
        self._main_frame.pack(fill="both", expand=True)
        self._main_frame.rowconfigure(1, weight=1)
        self._main_frame.columnconfigure(0, weight=1)
        self._main_frame.columnconfigure(1, weight=1)

        self._ticker_input = tk.Text(self._main_frame, width=40, height=5)
        self._ticker_input.grid(column=0, row=0)

        self._canvas = PlotCanvas(self._main_frame)
        self._canvas.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        ttk.Button(self._main_frame, text="Plot Stuff", command=self._execute).grid(column=1, row=1)

        self._period_options = ["Maximum", "10 years", "5 years", "1 year"]
        self._selected = StringVar(value="Maximum")
        OptionMenu(self._main_frame, self._selected, *self._period_options).grid(column=1, row=0)

    def _execute(self) -> None:
        u_input = (self._ticker_input.get("1.0", tk.END).strip()
                   .replace(" ", "").upper().split(","))

        try:
            self._dm.set_tickers(u_input)
            choice_map = {"Maximum": None,
                          "10 years": 120,
                          "5 years": 60,
                          "1 year": 12}

            period_in_months = choice_map[self._selected.get()]
            tickers_data = self._dm.calculate_or_fetch_index(period_in_months)
            self._canvas.plot_wealth_index(tickers_data)

        except ValueError as e:
            tk.messagebox.showerror("Error", str(e))


class PlotCanvas(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.canvas_widget = None

    def plot_wealth_index(self, wealth_index):
        if self.canvas_widget:
            plt.close('all')
            self.canvas_widget.get_tk_widget().destroy()

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.set_ylabel("Wealth Index")
        ax.grid(True)
        ax.set_title("Wealth Index Comparison")
        wealth_index.plot(ax=ax)

        self.canvas_widget = FigureCanvasTkAgg(fig, master=self)
        self.canvas_widget.draw()
        self.canvas_widget.get_tk_widget().pack(fill="both", expand=True)


if __name__ == "__main__":
    app = App()
    app.mainloop()
