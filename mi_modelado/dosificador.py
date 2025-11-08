import tkinter as tk
from tkinter import messagebox

class DosificadorConcreto:
    def __init__(self):
        self.ventana = tk.Tk()
        self.ventana.title("#80125 - Proyecto - Dosificador de Concreto by IA")
        self.ventana.geometry("400x500")
        
        # Variables para almacenar datos
        self.elemento = ""
        self.dimensiones = []
        self.resistencia = 210
        self.volumen = 0
        
        # Crear las pantallas
        self.crear_pantalla_inicio()
    
    def crear_pantalla_inicio(self):
        # Limpiar ventana
        for widget in self.ventana.winfo_children():
            widget.destroy()
        
        tk.Label(self.ventana, text="DOSIFICADOR DE CONCRETO", 
                font=("Arial", 16, "bold")).pack(pady=20)
        
        tk.Label(self.ventana, text="Selecciona el elemento:", 
                font=("Arial", 12)).pack(pady=10)
        
        # Lista de elementos usando un diccionario
        elementos = {
            "COLUMNA": "columna",
            "TRABE/VIGA": "trabe", 
            "LOSA": "losa",
            "MURO": "muro"
        }
        
        # Crear botones usando un ciclo
        for texto, valor in elementos.items():
            tk.Button(self.ventana, text=texto, width=20, height=2,
                     command=lambda v=valor: self.seleccionar_elemento(v)).pack(pady=5)
        
        # Botón de salir
        tk.Button(self.ventana, text="SALIR", width=20, height=2,
                 command=self.ventana.quit, bg="red", fg="white").pack(pady=10)
    
    def seleccionar_elemento(self, elemento):
        self.elemento = elemento
        self.crear_pantalla_dimensiones()
    
    def crear_pantalla_dimensiones(self):
        # Limpiar ventana
        for widget in self.ventana.winfo_children():
            widget.destroy()
        
        tk.Label(self.ventana, text=f"DIMENSIONES - {self.elemento.upper()}", 
                font=("Arial", 14, "bold")).pack(pady=10)
        
        # Definir etiquetas según el elemento
        if self.elemento == "columna":
            etiquetas = ["Largo (m):", "Ancho (m):", "Altura (m):"]
        elif self.elemento == "trabe":
            etiquetas = ["Base (m):", "Altura (m):", "Longitud (m):"]
        elif self.elemento == "losa":
            etiquetas = ["Largo (m):", "Ancho (m):", "Espesor (m):"]
        else:  # muro
            etiquetas = ["Largo (m):", "Altura (m):", "Espesor (m):"]
        
        # Crear campos de entrada usando un ciclo
        self.entradas = []
        for etiqueta in etiquetas:
            marco = tk.Frame(self.ventana)
            marco.pack(pady=5)
            tk.Label(marco, text=etiqueta, width=15).pack(side=tk.LEFT)
            entrada = tk.Entry(marco, width=10)
            entrada.pack(side=tk.LEFT)
            self.entradas.append(entrada)
        
        # Botones de navegación
        marco_botones = tk.Frame(self.ventana)
        marco_botones.pack(pady=20)
        
        tk.Button(marco_botones, text="← Atrás", 
                 command=self.crear_pantalla_inicio).pack(side=tk.LEFT, padx=10)
        
        tk.Button(marco_botones, text="Siguiente →", 
                 command=self.guardar_dimensiones).pack(side=tk.LEFT, padx=10)
    
    def guardar_dimensiones(self):
        try:
            # Obtener valores usando un ciclo
            self.dimensiones = []
            for entrada in self.entradas:
                valor = float(entrada.get())
                self.dimensiones.append(valor)
            
            # Calcular volumen (todos los elementos usan el mismo cálculo)
            self.volumen = self.dimensiones[0] * self.dimensiones[1] * self.dimensiones[2]
            
            self.crear_pantalla_resistencia()
            
        except ValueError:
            messagebox.showerror("Error", "Por favor ingresa números válidos")
    
    def crear_pantalla_resistencia(self):
        # Limpiar ventana
        for widget in self.ventana.winfo_children():
            widget.destroy()
        
        tk.Label(self.ventana, text="RESISTENCIA DEL CONCRETO", 
                font=("Arial", 14, "bold")).pack(pady=10)
        
        tk.Label(self.ventana, text=f"Volumen: {self.volumen:.3f} m³").pack(pady=5)
        
        # Lista de resistencias usando un diccionario
        resistencias = {
            "175 kg/cm² - Concreto pobre": 175,
            "210 kg/cm² - Normal": 210,
            "250 kg/cm² - Resistente": 250,
            "300 kg/cm² - Alta resistencia": 300
        }
        
        # Crear botones usando un ciclo
        for texto, valor in resistencias.items():
            tk.Button(self.ventana, text=texto, width=30, height=2,
                     command=lambda v=valor: self.seleccionar_resistencia(v)).pack(pady=5)
        
        # Botón de regreso
        tk.Button(self.ventana, text="← Atrás", 
                 command=self.crear_pantalla_dimensiones).pack(pady=10)
    
    def seleccionar_resistencia(self, resistencia):
        self.resistencia = resistencia
        self.mostrar_resultados()
    
    def mostrar_resultados(self):
        # Limpiar ventana
        for widget in self.ventana.winfo_children():
            widget.destroy()
        
        # Definir proporciones y relación a/c según resistencia
        if self.resistencia == 175:
            cemento, arena, grava, relacion_agua = 1, 2.5, 3.5, 0.55
        elif self.resistencia == 250:
            cemento, arena, grava, relacion_agua = 1, 1.5, 2.5, 0.45
        elif self.resistencia == 300:
            cemento, arena, grava, relacion_agua = 1, 1, 2, 0.36
        else:  # 210 por defecto
            cemento, arena, grava, relacion_agua = 1, 2, 3, 0.48
        
        # CÁLCULOS CORRECTOS SEGÚN MÉTODO DE LAS IMÁGENES
        # 1. Volumen seco total
        volumen_seco_total = self.volumen * 1.54
        
        # 2. Suma de proporciones
        suma_proporciones = cemento + arena + grava
        
        # 3. Volúmenes individuales
        volumen_cemento = volumen_seco_total * (cemento / suma_proporciones)
        volumen_arena = volumen_seco_total * (arena / suma_proporciones)
        volumen_grava = volumen_seco_total * (grava / suma_proporciones)
        
        # 4. Conversión a masa con densidades reales
        cemento_kg = volumen_cemento * 1440  # Densidad cemento: 1440 kg/m³
        arena_kg = volumen_arena * 1600      # Densidad arena: 1600 kg/m³
        grava_kg = volumen_grava * 1450      # Densidad grava: 1450 kg/m³
        
        # 5. Cálculo de agua
        agua_litros = cemento_kg * relacion_agua
        
        # 6. Unidades para comprar
        sacos_cemento = cemento_kg / 50
        arena_m3 = volumen_arena
        grava_m3 = volumen_grava
        
        # Mostrar resultados
        tk.Label(self.ventana, text="RESULTADOS FINALES", 
                font=("Arial", 16, "bold")).pack(pady=10)
        
        # Lista de textos a mostrar
        textos = [
            f"Elemento: {self.elemento.upper()}",
            f"Volumen concreto: {self.volumen:.3f} m³",
            f"Volumen seco total: {volumen_seco_total:.3f} m³",
            f"Resistencia: {self.resistencia} kg/cm²",
            f"Relación a/c: {relacion_agua}",
            "",
            "VOLÚMENES DE MATERIALES:",
            f"Cemento: {volumen_cemento:.4f} m³",
            f"Arena: {volumen_arena:.4f} m³", 
            f"Grava: {volumen_grava:.4f} m³",
            "",
            "MATERIALES REQUERIDOS:",
            f"Cemento: {cemento_kg:.1f} kg",
            f"Arena: {arena_kg:.1f} kg",
            f"Grava: {grava_kg:.1f} kg", 
            f"Agua: {agua_litros:.1f} litros",
            "",
            "PARA COMPRAR:",
            f"Sacos de cemento: {sacos_cemento:.1f}",
            f"Arena: {arena_m3:.3f} m³",
            f"Grava: {grava_m3:.3f} m³",
            "",
            f"PROPORCIÓN: {cemento}:{arena}:{grava}"
        ]
        
        # Mostrar textos usando un ciclo
        for texto in textos:
            tk.Label(self.ventana, text=texto, font=("Arial", 9)).pack(pady=1)
        
        # Botones finales
        marco_botones = tk.Frame(self.ventana)
        marco_botones.pack(pady=20)
        
        tk.Button(marco_botones, text="Nuevo Cálculo", 
                 command=self.crear_pantalla_inicio).pack(side=tk.LEFT, padx=10)
        
        tk.Button(marco_botones, text="Salir", 
                 command=self.ventana.quit, bg="red", fg="white").pack(side=tk.LEFT, padx=10)
    
    def ejecutar(self):
        self.ventana.mainloop()

# Ejecutar el programa
if __name__ == "__main__":
    app = DosificadorConcreto()
    app.ejecutar()
