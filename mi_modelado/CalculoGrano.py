#Leonardo Heredia Delgado


import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.ticker as ticker
from fpdf import FPDF
import os
from datetime import datetime

class CurvaGranulometricaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Análisis de Curva Granulométrica - Professional Edition")
        self.root.geometry("1400x900")
        self.setup_ui()
        
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame para entrada de datos
        input_frame = ttk.LabelFrame(main_frame, text="Ingreso de Datos", padding=10)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Ejemplos pre-cargados
        ejemplo_frame = ttk.Frame(input_frame)
        ejemplo_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(ejemplo_frame, text="Ejemplos rápidos:", font=("Arial", 9, "bold")).pack(side=tk.LEFT)
        
        # Botones de ejemplos pre-cargados
        ejemplos_frame = ttk.Frame(ejemplo_frame)
        ejemplos_frame.pack(side=tk.LEFT, padx=10)
        
        ejemplos = {
            "Suelo Arenoso": ("19,9.5,4.75,2.0,0.85,0.425,0.25,0.15,0.075", "0,15,45,80,120,150,100,60,30"),
            "Suelo Arcilloso": ("4.75,2.0,0.425,0.15,0.075,0.02,0.005,0.002", "5,10,25,40,60,80,50,30"),
            "Suelo Grava-Arena": ("75,38,19,9.5,4.75,2.0,0.425,0.075", "10,35,80,120,150,100,60,45"),
            "Suelo Bien Gradado": ("25,19,9.5,4.75,2.0,0.85,0.425,0.15,0.075,0.02", "5,15,40,75,100,120,90,60,40,20")
        }
        
        for nombre, (tamices, retenidos) in ejemplos.items():
            ttk.Button(ejemplos_frame, text=nombre, width=15,
                      command=lambda t=tamices, r=retenidos: self.cargar_ejemplo(t, r)).pack(side=tk.LEFT, padx=2)
        
        # Frame para tamices
        tamiz_frame = ttk.Frame(input_frame)
        tamiz_frame.pack(fill=tk.X, pady=5)
        ttk.Label(tamiz_frame, text="Tamices (mm):", width=15).pack(side=tk.LEFT)
        self.tamiz_entry = ttk.Entry(tamiz_frame, width=100)
        self.tamiz_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.tamiz_entry.insert(0, "75,63,50,38,25,19,9.5,4.75,2.0,0.425,0.075,0.002")
        
        # Frame para retenidos
        retenido_frame = ttk.Frame(input_frame)
        retenido_frame.pack(fill=tk.X, pady=5)
        ttk.Label(retenido_frame, text="Retenido (g):", width=15).pack(side=tk.LEFT)
        self.retenido_entry = ttk.Entry(retenido_frame, width=100)
        self.retenido_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.retenido_entry.insert(0, "0,0,15,35,80,120,150,180,200,150,80,20")
        
        # Botones principales
        button_frame = ttk.Frame(input_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="🔍 Generar Curva", 
                  command=self.generar_curva, style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🧹 Limpiar", 
                  command=self.limpiar_datos).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="💾 Guardar PNG", 
                  command=self.guardar_png).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📊 Generar PDF", 
                  command=self.generar_pdf).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="❌ Salir", 
                  command=self.root.quit).pack(side=tk.RIGHT, padx=5)
        
        # Frame para resultados y gráfica
        results_frame = ttk.Frame(main_frame)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame para tabla de resultados
        table_frame = ttk.LabelFrame(results_frame, text="Tabla de Resultados", padding=5)
        table_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Treeview para mostrar resultados
        columns = ("Tamiz", "Retenido", "%Ret", "%Pasa")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        scroll_tree = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_tree.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_tree.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Frame para gráfica
        graph_frame = ttk.LabelFrame(results_frame, text="Curva Granulométrica (Usa herramientas abajo para zoom)", padding=5)
        graph_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Figura de matplotlib
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # BARRA DE HERRAMIENTAS DE ZOOM - ¡ESTO ES LO NUEVO!
        toolbar_frame = ttk.Frame(graph_frame)
        toolbar_frame.pack(fill=tk.X)
        self.toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        self.toolbar.update()
        
        # Frame para resumen
        summary_frame = ttk.LabelFrame(main_frame, text="Resumen de Fracciones", padding=10)
        summary_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.summary_text = scrolledtext.ScrolledText(summary_frame, height=8, width=100, font=("Consolas", 9))
        self.summary_text.pack(fill=tk.BOTH, expand=True)
        
        # Variables para almacenar datos actuales
        self.current_data = None
        
        # Configurar estilo para botón destacado
        style = ttk.Style()
        style.configure("Accent.TButton", background="#4CAF50", foreground="black")
        
    def cargar_ejemplo(self, tamices, retenidos):
        self.tamiz_entry.delete(0, tk.END)
        self.retenido_entry.delete(0, tk.END)
        self.tamiz_entry.insert(0, tamices)
        self.retenido_entry.insert(0, retenidos)
        messagebox.showinfo("Ejemplo Cargado", "Datos de ejemplo cargados. Haz clic en 'Generar Curva' para visualizar.")
        
    def limpiar_datos(self):
        self.tamiz_entry.delete(0, tk.END)
        self.retenido_entry.delete(0, tk.END)
        self.tree.delete(*self.tree.get_children())
        self.ax.clear()
        self.canvas.draw()
        self.summary_text.delete(1.0, tk.END)
        self.current_data = None
        
    def guardar_png(self):
        if self.current_data is None:
            messagebox.showwarning("Advertencia", "Primero genera una curva para poder guardarla.")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
            title="Guardar gráfica como PNG"
        )
        
        if filename:
            try:
                self.fig.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
                messagebox.showinfo("Éxito", f"Gráfica guardada como:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar la gráfica:\n{str(e)}")
    
    def generar_pdf(self):
        if self.current_data is None:
            messagebox.showwarning("Advertencia", "Primero genera una curva para crear el PDF.")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            title="Guardar reporte como PDF"
        )
        
        if filename:
            try:
                self.crear_pdf_report(filename)
                messagebox.showinfo("Éxito", f"Reporte PDF guardado como:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo crear el PDF:\n{str(e)}")
    
    def crear_pdf_report(self, filename):
        pdf = FPDF()
        pdf.add_page()
        
        # Título
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "REPORTE DE ANÁLISIS GRANULOMÉTRICO", 0, 1, 'C')
        pdf.ln(5)
        
        # Fecha
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(0, 10, f"Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1, 'C')
        pdf.ln(10)
        
        # Datos de entrada
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "DATOS DE ENTRADA:", 0, 1)
        pdf.set_font("Arial", '', 10)
        pdf.cell(0, 10, f"Tamices (mm): {self.tamiz_entry.get()}", 0, 1)
        pdf.cell(0, 10, f"Retenidos (g): {self.retenido_entry.get()}", 0, 1)
        pdf.ln(5)
        
        # Resultados
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "RESULTADOS:", 0, 1)
        pdf.set_font("Arial", '', 10)
        
        data = self.current_data
        pdf.cell(0, 10, f"Material total analizado: {data['total']:.1f} g", 0, 1)
        pdf.cell(0, 10, f"Grava (>2.0 mm): {data['grava_pct']:.2f}%", 0, 1)
        pdf.cell(0, 10, f"Arena (2.0 - 0.075 mm): {data['arena_pct']:.2f}%", 0, 1)
        pdf.cell(0, 10, f"Limo (0.075 - 0.002 mm): {data['limo_pct']:.2f}%", 0, 1)
        pdf.cell(0, 10, f"Arcilla (<0.002 mm): {data['arcilla_pct']:.2f}%", 0, 1)
        pdf.ln(5)
        
        # Clasificación
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "CLASIFICACIÓN:", 0, 1)
        pdf.set_font("Arial", '', 10)
        pdf.multi_cell(0, 10, data['clasificacion'])
        
        # Guardar gráfica temporalmente
        temp_img = "temp_curve.png"
        self.fig.savefig(temp_img, dpi=150, bbox_inches='tight')
        
        # Agregar imagen al PDF
        pdf.add_page()
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "CURVA GRANULOMÉTRICA:", 0, 1)
        pdf.image(temp_img, x=10, y=30, w=180)
        
        pdf.output(filename)
        
        # Eliminar archivo temporal
        try:
            os.remove(temp_img)
        except:
            pass
    
    def generar_curva(self):
        try:
            tamices_str = self.tamiz_entry.get()
            retenido_str = self.retenido_entry.get()
            
            if not tamices_str or not retenido_str:
                messagebox.showerror("Error", "Por favor ingrese datos en ambos campos")
                return
            
            tamices = np.array([float(x.strip()) for x in tamices_str.split(",")])
            retenido = np.array([float(x.strip()) for x in retenido_str.split(",")])
            
            if len(tamices) != len(retenido):
                messagebox.showerror("Error", "La cantidad de tamices y retenidos no coincide")
                return
            
            self.procesar_datos(tamices, retenido)
            
        except ValueError as e:
            messagebox.showerror("Error", f"Error en formato de datos: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado: {str(e)}")
    
    def procesar_datos(self, tamices, retenido):
        ord_desc = np.argsort(tamices)[::-1]
        tamices = tamices[ord_desc]
        retenido = retenido[ord_desc]
        
        total = retenido.sum()
        porc_ret = retenido / total * 100
        porc_ret_acu = np.cumsum(porc_ret)
        porc_pasa = 100 - porc_ret_acu
        
        lim_grava_arena = 2.0
        lim_arena_limo = 0.075
        lim_limo_arcilla = 0.002
        
        def porc_pasa_en(limite):
            if limite >= tamices.max():
                return porc_pasa[0]
            if limite <= tamices.min():
                return porc_pasa[-1]
            return float(np.interp(limite, tamices[::-1], porc_pasa[::-1]))
        
        p_at_2mm = porc_pasa_en(lim_grava_arena)
        p_at_075 = porc_pasa_en(lim_arena_limo)
        p_at_0002 = porc_pasa_en(lim_limo_arcilla)
        
        grava_pct = 100.0 - p_at_2mm
        arena_pct = p_at_2mm - p_at_075
        limo_pct = p_at_075 - p_at_0002
        arcilla_pct = p_at_0002
        
        # Clasificación
        if grava_pct > 50:
            clasif = "Material principalmente granular (Grava)"
        elif arena_pct > 50:
            clasif = "Material principalmente arenoso"
        elif limo_pct > 50:
            clasif = "Material principalmente limoso"
        elif arcilla_pct > 50:
            clasif = "Material principalmente arcilloso"
        elif arena_pct + grava_pct > 50:
            clasif = "Material granular (Suelo grueso)"
        else:
            clasif = "Material fino (Limo/Arcilla)"
        
        # Guardar datos actuales
        self.current_data = {
            'tamices': tamices, 'retenido': retenido, 'porc_ret': porc_ret, 
            'porc_pasa': porc_pasa, 'total': total, 'grava_pct': grava_pct,
            'arena_pct': arena_pct, 'limo_pct': limo_pct, 'arcilla_pct': arcilla_pct,
            'clasificacion': clasif
        }
        
        self.actualizar_tabla(tamices, retenido, porc_ret, porc_pasa)
        self.generar_grafica(tamices, porc_pasa, total)
        self.actualizar_resumen(total, grava_pct, arena_pct, limo_pct, arcilla_pct, clasif)
    
    def actualizar_tabla(self, tamices, retenido, porc_ret, porc_pasa):
        self.tree.delete(*self.tree.get_children())
        
        for t, r, pr, pp in zip(tamices, retenido, porc_ret, porc_pasa):
            self.tree.insert("", tk.END, values=(f"{t:.3f}", f"{r:.1f}", f"{pr:.2f}", f"{pp:.2f}"))
    
    def generar_grafica(self, tamices, porc_pasa, total):
        self.ax.clear()
        
        lim_grava_arena = 2.0
        lim_arena_limo = 0.075
        lim_limo_arcilla = 0.002
        
        # Bandas de colores
        self.ax.axvspan(tamices.max()*1.1, lim_grava_arena, color="#d0f0c0", alpha=0.4, label="Grava")
        self.ax.axvspan(lim_grava_arena, lim_arena_limo, color="#fff2a8", alpha=0.35, label="Arena")
        self.ax.axvspan(lim_arena_limo, lim_limo_arcilla, color="#cfe8ff", alpha=0.25, label="Limo")
        self.ax.axvspan(lim_limo_arcilla, tamices.min()*0.9, color="#f6d4f6", alpha=0.4, label="Arcilla")
        
        # Curva granulométrica
        self.ax.plot(tamices, porc_pasa, marker="o", linewidth=2, label="% que pasa", color="red", markersize=6)
        
        # Líneas verticales de separación
        for x in [lim_grava_arena, lim_arena_limo, lim_limo_arcilla]:
            self.ax.axvline(x, color="k", linestyle="--", linewidth=0.9)
        
        # Etiquetas
        def log_mid(a, b):
            return 10 ** ((np.log10(a) + np.log10(b)) / 2.0)
        
        x_g = log_mid(tamices.max(), lim_grava_arena)
        x_a = log_mid(lim_grava_arena, lim_arena_limo)
        x_l = log_mid(lim_arena_limo, lim_limo_arcilla)
        x_c = log_mid(lim_limo_arcilla, tamices.min())
        
        
        y_label = 8
        self.ax.text(x_g, y_label, "Grava", ha="center", va="center", fontsize=11, fontweight="bold")
        self.ax.text(x_a, y_label, "Arena", ha="center", va="center", fontsize=11, fontweight="bold")
        self.ax.text(x_l, y_label, "Limo", ha="center", va="center", fontsize=11, fontweight="bold")
        self.ax.text(x_c, y_label, "Arcilla", ha="center", va="center", fontsize=11, fontweight="bold")
        
        # Formato de ejes
        self.ax.invert_xaxis()
        self.ax.set_xscale("log")
        self.ax.grid(True, which="both", linestyle="--", alpha=0.5)
        self.ax.set_xticks(tamices)
        self.ax.set_xticklabels([f"{t}" for t in tamices], rotation=45)
        self.ax.set_xlabel("Tamaño del tamiz (mm)", fontsize=12)
        self.ax.set_ylabel("% que pasa", fontsize=12)
        self.ax.set_title(f"Curva Granulométrica - Total: {total:.1f} g", fontsize=14, fontweight="bold")
        self.ax.set_ylim(0, 100)
        
        self.fig.tight_layout()
        self.canvas.draw()
    
    def actualizar_resumen(self, total, grava_pct, arena_pct, limo_pct, arcilla_pct, clasif):
        texto = f"""Material total analizado: {total:.1f} g

PORCENTAJE POR FRACCIÓN:
────────────────────────────────────────
Grava (>2.0 mm):        {grava_pct:>6.2f}%
Arena (2.0 - 0.075 mm): {arena_pct:>6.2f}%
Limo (0.075 - 0.002 mm):{limo_pct:>6.2f}%
Arcilla (<0.002 mm):    {arcilla_pct:>6.2f}%

CLASIFICACIÓN:
────────────────────────────────────────
{clasif}

INSTRUCCIONES ZOOM:
────────────────────────────────────────
• Usa las herramientas arriba de la gráfica
• 📊: Zoom rectangular
• 🏠: Restablecer vista original
• 🧭: Pan/arrastrar
• 🔧: Configurar subgráficas"""

        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(1.0, texto)

def main():
    root = tk.Tk()
    app = CurvaGranulometricaApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
