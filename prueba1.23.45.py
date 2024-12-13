import os
import json
import tkinter as tk
from tkinter import messagebox, simpledialog, Toplevel
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from itertools import product

class SistemaExpertoDolores:
    def __init__(self, reglas_file="reglas_dolores.json"):
        self.reglas_file = reglas_file
        self.cargar_reglas()
        self.root = tk.Tk()
        self.root.title("Sistema Experto - Diagnóstico de Dolores")
        self.crear_interfaz()
        self.root.geometry("800x600")
        self.root.mainloop()

    def cargar_reglas(self):
        if os.path.exists(self.reglas_file):
            with open(self.reglas_file, "r", encoding="utf-8") as file:
                try:
                    self.reglas = json.load(file)
                except json.JSONDecodeError:
                    self.reglas = {}
        else:
            self.reglas = {}

    def guardar_reglas(self):
        with open(self.reglas_file, "w", encoding="utf-8") as file:
            json.dump(self.reglas, file, ensure_ascii=False, indent=4)

    def salir(self):
        self.root.destroy()

    def crear_interfaz(self):
        frame = tk.Frame(self.root)
        frame.pack(expand=True, fill=tk.BOTH)

        tk.Label(frame, text="Sistema Experto - Diagnóstico de Dolores", font=("Helvetica", 16, "bold")).pack(pady=20)

        botones = [
            ("Diagnosticar Dolor", self.nuevo_diagnostico),
            ("Ver Árbol de Decisiones", self.ver_arbol_decisiones),
            ("Generar Tablas de Verdad", self.generar_tablas_verdad_por_lugar),
            ("Generar Mapa Semántico", self.generar_mapa_semantico),
            ("Salir", self.salir),
        ]

        for texto, comando in botones:
            boton = tk.Button(frame, text=texto, font=("Helvetica", 14), command=comando, height=2, width=25)
            boton.pack(pady=10)

    def nuevo_diagnostico(self):
        lugar = self.seleccionar_lugar()
        if lugar not in self.reglas:
            self.ofrecer_agregar_lugar(lugar)
        else:
            self.navegar_preguntas(self.reglas[lugar], lugar)

    def seleccionar_lugar(self):
        lugar = simpledialog.askstring("Lugar del Dolor", "¿Dónde siente el dolor?")
        return lugar.lower() if lugar else ""

    def ofrecer_agregar_lugar(self, lugar):
        agregar = messagebox.askyesno("Agregar Nuevo Lugar", f"El lugar '{lugar}' no está registrado. ¿Desea agregarlo?")
        if agregar:
            self.agregar_lugar(lugar)

    def agregar_lugar(self, lugar):
        nueva_pregunta = simpledialog.askstring("Nueva Pregunta", f"Ingrese una pregunta inicial para '{lugar}':")
        if nueva_pregunta:
            nuevo_diagnostico = simpledialog.askstring("Nuevo Diagnóstico", "Ingrese el diagnóstico para la respuesta 'sí':")
            if nuevo_diagnostico:
                self.reglas[lugar] = {
                    nueva_pregunta: {"sí": nuevo_diagnostico, "no": {}}
                }
                self.guardar_reglas()
                messagebox.showinfo("Éxito", "Nuevo lugar, pregunta y diagnóstico agregados exitosamente.")

    def navegar_preguntas(self, nodo_actual, lugar):
        camino = []

        while isinstance(nodo_actual, dict) and nodo_actual:
            pregunta, subnodo = next(iter(nodo_actual.items()))
            respuesta = messagebox.askyesno("Pregunta", pregunta)
            camino.append((pregunta, respuesta))

            if respuesta:
                nodo_actual = subnodo.get("sí", {})
            else:
                nodo_actual = subnodo.get("no", {})

        if isinstance(nodo_actual, str) and nodo_actual:
            messagebox.showinfo("Diagnóstico", f"Diagnóstico: {nodo_actual}")
        else:
            self.ofrecer_agregar_pregunta_o_diagnostico(camino, nodo_actual, lugar)

    def ofrecer_agregar_pregunta_o_diagnostico(self, camino, nodo_actual, lugar):
        agregar = messagebox.askyesno("Agregar Pregunta/Diagnóstico", "No se encontró un diagnóstico adecuado. ¿Desea agregar uno nuevo?")
        if agregar:
            self.agregar_pregunta_y_diagnostico(camino, nodo_actual, lugar)

    def agregar_pregunta_y_diagnostico(self, camino, nodo_actual, lugar):
        nueva_pregunta = simpledialog.askstring("Nueva Pregunta", "Ingrese una nueva pregunta:")
        if nueva_pregunta:
            nuevo_diagnostico = simpledialog.askstring("Nuevo Diagnóstico", "Ingrese el diagnóstico para la respuesta 'sí':")
            if nuevo_diagnostico:
                nodo = self.reglas[lugar]  # Navegar dentro del lugar específico
                for pregunta, respuesta in camino:
                    if pregunta not in nodo:
                        nodo[pregunta] = {"sí": {}, "no": {}}
                    nodo = nodo[pregunta]["sí" if respuesta else "no"]
                nodo[nueva_pregunta] = {"sí": nuevo_diagnostico, "no": {}}
                self.guardar_reglas()
                messagebox.showinfo("Éxito", "Nueva pregunta y diagnóstico agregados exitosamente.")

    def ver_arbol_decisiones(self):
        if not self.reglas:
            messagebox.showerror("Error", "No hay reglas definidas para mostrar el árbol.")
            return

        ventana = Toplevel(self.root)
        ventana.title("Árbol de Decisiones")
        ventana.geometry("1000x800")

        fig = Figure(figsize=(12, 10))
        ax = fig.add_subplot(111)
        ax.axis("off")

        y_inicio = 1
        for i, (lugar, subnodo) in enumerate(self.reglas.items()):
            x_inicio = 0.5
            self.dibujar_arbol({lugar: subnodo}, ax, x_inicio, y_inicio, 0.2, 0.15, es_raiz=True)
            y_inicio -= 1

        canvas = FigureCanvasTkAgg(fig, master=ventana)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def dibujar_arbol(self, nodo, ax, x, y, dx, dy, es_raiz=False):
        if isinstance(nodo, dict):
            for pregunta, subnodo in nodo.items():
                color = "yellow" if es_raiz else "lightblue"
                ax.text(x, y, pregunta, ha="center", va="center", bbox=dict(boxstyle="round", facecolor=color))

                if isinstance(subnodo, dict) and "sí" in subnodo:
                    x_sí = x - dx
                    y_sí = y - dy
                    ax.plot([x, x_sí], [y, y_sí], "k-")
                    self.dibujar_arbol(subnodo["sí"], ax, x_sí, y_sí, dx / 2, dy)

                if isinstance(subnodo, dict) and "no" in subnodo:
                    x_no = x + dx
                    y_no = y - dy
                    ax.plot([x, x_no], [y, y_no], "k-")
                    self.dibujar_arbol(subnodo["no"], ax, x_no, y_no, dx / 2, dy)

                elif isinstance(subnodo, dict):
                    self.dibujar_arbol(subnodo, ax, x, y - dy, dx / 2, dy)
        elif isinstance(nodo, str):
            ax.text(x, y, nodo, ha="center", va="center", bbox=dict(boxstyle="round", facecolor="lightgreen"))

    def generar_tablas_verdad_por_lugar(self):
        if not self.reglas:
            messagebox.showerror("Error", "No hay reglas definidas para generar las tablas de verdad.")
            return

        def extraer_preguntas(nodo, preguntas):
            if isinstance(nodo, dict):
                for pregunta, subnodo in nodo.items():
                    preguntas.add(pregunta)
                    if isinstance(subnodo, dict):
                        extraer_preguntas(subnodo, preguntas)

        def evaluar_respuestas(nodo, respuestas):
            if isinstance(nodo, dict):
                for pregunta, subnodo in nodo.items():
                    respuesta = respuestas.get(pregunta, "no")
                    if respuesta in subnodo:
                        return evaluar_respuestas(subnodo[respuesta], respuestas)
                    else:
                        return False
            elif isinstance(nodo, str):
                return True
            return False

        for lugar, arbol in self.reglas.items():
            preguntas = set()
            extraer_preguntas(arbol, preguntas)

            preguntas = sorted(preguntas)
            combinaciones = list(product(["sí", "no"], repeat=len(preguntas)))
            resultados = []

            for combinacion in combinaciones:
                respuestas = dict(zip(preguntas, combinacion))
                resultado = evaluar_respuestas(arbol, respuestas)
                resultados.append({**respuestas, "Resultado": resultado})

            df = pd.DataFrame(resultados)

            ventana = Toplevel(self.root)
            ventana.title(f"Tabla de Verdad - {lugar.capitalize()}")
            ventana.geometry("1000x600")

            from pandastable import Table

            frame = tk.Frame(ventana)
            frame.pack(fill=tk.BOTH, expand=True)

            pt = Table(frame, dataframe=df, showtoolbar=True, showstatusbar=True)
            pt.show()

    def generar_mapa_semantico(self):
        if not self.reglas:
            messagebox.showerror("Error", "No hay reglas definidas para generar el mapa semántico.")
            return

        ventana = Toplevel(self.root)
        ventana.title("Mapa Semántico")
        ventana.geometry("1000x800")

        fig = Figure(figsize=(12, 10))
        ax = fig.add_subplot(111)
        ax.axis("off")

        def dibujar_mapa(nodo, ax, x, y, dx, dy):
            if isinstance(nodo, dict):
                for pregunta, subnodo in nodo.items():
                    ax.text(x, y, pregunta, ha="center", va="center", bbox=dict(boxstyle="round", facecolor="lightblue"))
                    if isinstance(subnodo, dict):
                        if "sí" in subnodo:
                            x_sí = x - dx
                            y_sí = y - dy
                            ax.plot([x, x_sí], [y, y_sí], "k-")
                            dibujar_mapa(subnodo["sí"], ax, x_sí, y_sí, dx / 2, dy)
                        if "no" in subnodo:
                            x_no = x + dx
                            y_no = y - dy
                            ax.plot([x, x_no], [y, y_no], "k-")
                            dibujar_mapa(subnodo["no"], ax, x_no, y_no, dx / 2, dy)
                    elif isinstance(subnodo, str):
                        ax.text(x, y - dy, subnodo, ha="center", va="center", bbox=dict(boxstyle="round", facecolor="lightgreen"))

        y_inicio = 1
        for lugar, subnodo in self.reglas.items():
            ax.text(0.5, y_inicio, lugar, ha="center", va="center", bbox=dict(boxstyle="round", facecolor="yellow"))
            dibujar_mapa(subnodo, ax, 0.5, y_inicio - 0.1, 0.2, 0.15)
            y_inicio -= 1

        canvas = FigureCanvasTkAgg(fig, master=ventana)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    if not os.path.exists("reglas_dolores.json"):
        reglas_iniciales = {}
        with open("reglas_dolores.json", "w", encoding="utf-8") as file:
            json.dump(reglas_iniciales, file, ensure_ascii=False, indent=4)

    SistemaExpertoDolores()
