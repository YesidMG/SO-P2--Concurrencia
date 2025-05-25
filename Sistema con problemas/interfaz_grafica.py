import tkinter as tk 
from tkinter import ttk, messagebox, scrolledtext 
import threading 
import logging
from enums import Estado

class InterfazGrafica:
    def __init__(self, root, sistema):
        """
        Inicializa la interfaz gráfica para visualizar el sistema de gestión de recursos.
        Configura la ventana principal, estilos y crea la interfaz de selección inicial.
        """
        self.root = root
        self.sistema = sistema
        self.sistema.configurar_interfaz(self)

        self.root.title("Sistema de Gestión de Recursos de Laboratorio")
        ancho_pantalla = self.root.winfo_screenwidth()
        alto_pantalla = self.root.winfo_screenheight()
        ancho_ventana = int(ancho_pantalla * 0.9)
        alto_ventana = int(alto_pantalla * 0.9)
        pos_x = (ancho_pantalla - ancho_ventana) // 2
        pos_y = (alto_pantalla - alto_ventana) // 2
        self.root.geometry(f"{ancho_ventana}x{alto_ventana}+{pos_x}+{pos_y-30}")
        self.root.minsize(800, 600) 
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)
        
        self.configurar_estilos()
        
        self.frames_estudiantes = {}
        self.etiquetas_recursos = {}
        
        self.simulacion_activa = False
        
        self.crear_interfaz_seleccion()
    
    def configurar_estilos(self):
        """
        Configura los estilos modernos para todos los componentes de la interfaz,
        incluyendo colores, fuentes y efectos visuales para botones y frames.
        """
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        self.color_primario = "#2C3E50"
        self.color_secundario = "#3498DB"
        self.color_acento = "#E74C3C"
        self.color_exito = "#27AE60"
        self.color_fondo = "#ECF0F1"
        
        estilos_botones = {
            "Principal.TButton": (self.color_secundario, "#2980B9", "#21618C", (20, 15), 11),
            "Accion.TButton": (self.color_exito, "#229954", "#1E8449", (15, 10), 10),
            "Peligro.TButton": (self.color_acento, "#C0392B", "#A93226", (15, 10), 10)
        }
        
        for style_name, (bg, active_bg, pressed_bg, padding, font_size) in estilos_botones.items():
            self.style.configure(style_name, padding=padding, font=("Segoe UI", font_size, "bold"), background=bg, foreground="white", borderwidth=0, focuscolor="none")
            self.style.map(style_name, background=[("active", active_bg), ("pressed", pressed_bg)])
        
        self.style.configure("Moderno.TLabelframe", background=self.color_fondo, borderwidth=2, relief="solid")
        self.style.configure("Moderno.TLabelframe.Label", font=("Segoe UI", 12, "bold"), background=self.color_fondo, foreground=self.color_primario)
        
        self.root.configure(bg=self.color_fondo)
    
    def crear_interfaz_seleccion(self):
        """
        Crea la interfaz de selección de problemas con diseño moderno.
        Permite al usuario elegir entre diferentes tipos de problemas de concurrencia.
        """
        if hasattr(self, 'marco_seleccion'):
            try:
                if self.marco_seleccion.winfo_exists():
                    self.marco_seleccion.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
                    return
            except tk.TclError:
                delattr(self, 'marco_seleccion')
    
        self.marco_seleccion = tk.Frame(self.root, bg=self.color_fondo)
        self.marco_seleccion.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        contenedor_central = tk.Frame(self.marco_seleccion, bg="white", relief="raised", borderwidth=2)
        contenedor_central.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        self.crear_header(contenedor_central)
        
        self.crear_tarjetas_problemas(contenedor_central)
        
        btn_frame = tk.Frame(contenedor_central, bg="white")
        btn_frame.pack(pady=(20, 10))
        
        ttk.Button(btn_frame, text="❌ Salir", command=self.cerrar_aplicacion, style="Peligro.TButton").pack()
    
    def crear_header(self, parent):
        """
        Crea el encabezado principal de la aplicación con título y subtítulo.
        """
        header_frame = tk.Frame(parent, bg="#2C3E50", height=70)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="🔬 Sistema de Gestión de Recursos de Laboratorio", font=("Segoe UI", 18, "bold"), bg="#2C3E50", fg="white").pack(pady=15)
        
        subtitulo_frame = tk.Frame(parent, bg="white")
        subtitulo_frame.pack(pady=(0, 15))
        
        tk.Label(subtitulo_frame, text="⚙️ Simulador de Problemas de Concurrencia", font=("Segoe UI", 13), bg="white", fg="#7F8C8D").pack()
        
        tk.Label(parent, text="Selecciona el tipo de problema que deseas simular:", font=("Segoe UI", 11), bg="white", fg="#2C3E50").pack(pady=(0, 20))
    
    def crear_tarjetas_problemas(self, parent):
        """
        Crea las tarjetas de selección para cada tipo de problema de concurrencia.
        Cada tarjeta incluye icono, descripción y botón para iniciar la simulación.
        """
        tarjetas_frame = tk.Frame(parent, bg="white")
        tarjetas_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)
        
        for i in range(3):
            tarjetas_frame.grid_columnconfigure(i, weight=1)
        tarjetas_frame.grid_rowconfigure(0, weight=1)
        
        problemas = [
            ("🔒", "Interbloqueo", "Deadlock", 
             "Los estudiantes solicitarán recursos\nen orden diferente, causando\nbloqueo mutuo permanente.",
             "#E74C3C", "interbloqueo"),
            ("⏳", "Inanición", "Starvation",
             "Algunos estudiantes tendrán\nbaja prioridad y podrían no\nobtener recursos durante mucho tiempo.",
             "#F39C12", "inanicion"),
            ("🏃", "Condiciones de Carrera", "Race Conditions",
             "Múltiples estudiantes competirán\npor recursos sin sincronización\nadecuada, causando inconsistencias.",
             "#9B59B6", "condiciones_carrera")
        ]
        
        for i, (icono, titulo, subtitulo, descripcion, color, tipo) in enumerate(problemas):
            self.crear_tarjeta_problema(tarjetas_frame, 0, i, icono, titulo, subtitulo, descripcion, color, tipo)
    
    def crear_tarjeta_problema(self, parent, row, col, icono, titulo, subtitulo, descripcion, color, tipo_problema):
        """
        Crea una tarjeta individual para un tipo específico de problema.
        Incluye efectos hover y funcionalidad clickeable para iniciar la simulación.
        """
        tarjeta = tk.Frame(parent, bg="white", relief="raised", borderwidth=1)
        tarjeta.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        def on_enter(e): tarjeta.configure(relief="raised", borderwidth=3)
        def on_leave(e): tarjeta.configure(relief="raised", borderwidth=1)
        
        header = tk.Frame(tarjeta, bg=color, height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text=icono, font=("Segoe UI", 20), bg=color, fg="white").pack(pady=8)
        
        contenido = tk.Frame(tarjeta, bg="white")
        contenido.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        tk.Label(contenido, text=titulo, font=("Segoe UI", 12, "bold"), bg="white", fg="#2C3E50").pack()
        
        tk.Label(contenido, text=f"({subtitulo})", font=("Segoe UI", 9, "italic"), bg="white", fg="#7F8C8D").pack(pady=(0, 8))
        
        tk.Label(contenido, text=descripcion, font=("Segoe UI", 8), bg="white", fg="#34495E", justify=tk.CENTER).pack(pady=(0, 15))
        
        ttk.Button(contenido, text="Iniciar", command=lambda: self.iniciar_simulacion_problema(tipo_problema), style="Principal.TButton").pack()
        
        widgets = [tarjeta, header, contenido]
        for widget in widgets:
            widget.bind("<Button-1>", lambda e: self.iniciar_simulacion_problema(tipo_problema))
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
    
    def crear_interfaz_simulacion(self):
        """
        Crea la interfaz principal de simulación con tres secciones:
        estudiantes, recursos y logs de eventos.
        """
        self.marco_principal = tk.Frame(self.root, bg=self.color_fondo)
        self.marco_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        header_sim = tk.Frame(self.marco_principal, bg="#34495E", height=50)
        header_sim.pack(fill=tk.X, pady=(0, 10))
        header_sim.pack_propagate(False)
        
        tk.Label(header_sim, text="🔬 Simulación en Progreso", font=("Segoe UI", 14, "bold"), bg="#34495E", fg="white").pack(pady=10)
        
        contenido_principal = tk.Frame(self.marco_principal, bg=self.color_fondo)
        contenido_principal.pack(fill=tk.BOTH, expand=True)
        
        for i, (weight, minsize) in enumerate([(3, 490), (1, 250), (2, 450)]):
            contenido_principal.grid_columnconfigure(i, weight=weight, minsize=minsize)
        contenido_principal.grid_rowconfigure(0, weight=1)
        
        self.crear_seccion_estudiantes(contenido_principal)
        self.crear_seccion_recursos(contenido_principal)
        self.crear_seccion_log(contenido_principal)
        
        self.crear_botones_control()
        
        self.root.after(100, self.actualizar_tiempos)
    
    def crear_seccion_estudiantes(self, parent):
        """
        Crea la sección que muestra la información de todos los estudiantes
        en el laboratorio con scroll vertical para múltiples estudiantes.
        """
        self.marco_estudiantes = ttk.LabelFrame(parent, text="👨‍🎓 Estudiantes del Laboratorio", style="Moderno.TLabelframe", padding="10")
        self.marco_estudiantes.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        self.canvas_estudiantes, self.scroll_frame_estudiantes = self.crear_canvas_con_scroll(self.marco_estudiantes)
    
    def crear_seccion_recursos(self, parent):
        """
        Crea la sección que muestra el estado de todos los recursos disponibles
        en el laboratorio con scroll vertical para múltiples recursos.
        """
        self.marco_recursos = ttk.LabelFrame(parent, text="🔧 Recursos Disponibles", style="Moderno.TLabelframe", padding="10")
        self.marco_recursos.grid(row=0, column=1, sticky="nsew", padx=5)
        
        self.canvas_recursos, self.scroll_frame_recursos = self.crear_canvas_con_scroll(self.marco_recursos)
    
    def crear_seccion_log(self, parent):
        """
        Crea la sección que muestra el registro de eventos en tiempo real
        durante la simulación con scroll automático.
        """
        self.marco_log = ttk.LabelFrame(parent, text="📋 Registro de Eventos", style="Moderno.TLabelframe", padding="10")
        self.marco_log.grid(row=0, column=2, sticky="nsew", padx=(5, 0))
        
        self.texto_log = scrolledtext.ScrolledText(self.marco_log, wrap=tk.WORD, height=20, font=("Consolas", 8), bg="#2C3E50", fg="#ECF0F1", insertbackground="white", selectbackground="#3498DB")
        self.texto_log.pack(fill=tk.BOTH, expand=True)
    
    def crear_canvas_con_scroll(self, parent):
        """
        Crea un canvas con scrollbar vertical para manejar contenido dinámico
        que puede exceder el espacio visible disponible.
        """
        canvas = tk.Canvas(parent, bg="white")
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="white")
        
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        return canvas, scroll_frame
    
    def crear_botones_control(self):
        """
        Crea los botones de control para la simulación, incluyendo
        opciones para volver al menú principal y cerrar la aplicación.
        """
        self.marco_botones = tk.Frame(self.marco_principal, bg=self.color_fondo, height=60)
        self.marco_botones.pack(fill=tk.X, pady=(10, 0))
        self.marco_botones.pack_propagate(False)
        
        tk.Frame(self.marco_botones, height=1, bg="#BDC3C7").pack(fill=tk.X, pady=(5, 10))
        
        botones_frame = tk.Frame(self.marco_botones, bg=self.color_fondo)
        botones_frame.pack(pady=5)
        
        self.btn_volver = ttk.Button(botones_frame, text="🔙 Volver al Menú", command=self.volver_menu, style="Accion.TButton")
        self.btn_volver.pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Button(botones_frame, text="❌ Cerrar", command=self.cerrar_aplicacion, style="Peligro.TButton").pack(side=tk.LEFT)
    
    def safe_thread_execute(self, func):
        """
        Ejecuta una función de forma thread-safe usando el método after de tkinter
        para evitar problemas de concurrencia en la interfaz gráfica.
        """
        try:
            self.root.after(0, func)
        except (tk.TclError, RuntimeError):
            pass
    
    def iniciar_simulacion_problema(self, tipo_problema):
        """
        Inicia la simulación del tipo de problema especificado, configurando
        la interfaz y ejecutando la simulación en un hilo separado.
        """
        if self.simulacion_activa:
            messagebox.showwarning("Simulación en Curso", "Ya hay una simulación ejecutándose. Espera a que termine.")
            return
        
        self.simulacion_activa = True
        self.marco_seleccion.pack_forget()
        self.crear_interfaz_simulacion()
        
        info_problema = {
            "interbloqueo": "🔒 SIMULANDO INTERBLOQUEO: Los estudiantes solicitarán recursos en orden diferente, causando bloqueo mutuo.",
            "inanicion": "⏳ SIMULANDO INANICIÓN: Algunos estudiantes tendrán baja prioridad y podrían no obtener recursos.",
            "condiciones_carrera": "🏃 SIMULANDO CONDICIONES DE CARRERA: Múltiples estudiantes competirán por recursos sin sincronización adecuada."
        }
        
        logging.info("=" * 80)
        logging.info(info_problema[tipo_problema])
        logging.info("=" * 80)
        
        self.limpiar_simulacion_anterior()
        self.sistema.recursos.clear()
        self.sistema.estudiantes.clear()
        self.sistema.inicializar_recursos()
        self.inicializar_vista_recursos()
        
        threading.Thread(target=self.ejecutar_simulacion_problema, args=(tipo_problema,), daemon=True).start()
    
    def ejecutar_simulacion_problema(self, tipo_problema):
        """
        Ejecuta la simulación del problema especificado en un hilo separado,
        gestionando errores y finalizando correctamente la simulación.
        """
        try:
            simulaciones = {
                "interbloqueo": lambda: self.sistema.iniciar_simulacion_interbloqueo(num_estudiantes=4),
                "inanicion": lambda: self.sistema.iniciar_simulacion_inanicion(num_estudiantes=6),
                "condiciones_carrera": lambda: self.sistema.iniciar_simulacion_condiciones_carrera(num_estudiantes=5)
            }
            
            simulaciones[tipo_problema]()
            
            for estudiante in self.sistema.estudiantes:
                estudiante.join()
            
        except Exception as e:
            logging.error(f"Error en la simulación: {e}")
            self.safe_thread_execute(lambda: messagebox.showerror("Error", f"Ocurrió un error durante la simulación: {str(e)}"))
        finally:
            self.simulacion_activa = False
    
    def volver_menu(self):
        """
        Vuelve al menú principal en cualquier momento, finalizando la simulación
        actual y limpiando todos los recursos y hilos activos.
        """
        try:
            self.simulacion_activa = False
            
            if hasattr(self, 'sistema'):
                self.sistema.finalizar()
                
            if hasattr(self.sistema, 'estudiantes'):
                for estudiante in self.sistema.estudiantes:
                    if estudiante.is_alive():
                        estudiante.debe_terminar = True
            
            self.limpiar_simulacion_anterior()
            
            if hasattr(self, 'marco_principal'):
                try:
                    self.marco_principal.destroy()
                    delattr(self, 'marco_principal')
                except:
                    pass
            
            for attr in ['canvas_estudiantes', 'scroll_frame_estudiantes', 'canvas_recursos', 'scroll_frame_recursos', 'texto_log', 'marco_botones']:
                if hasattr(self, attr):
                    try:
                        delattr(self, attr)
                    except:
                        pass
            
            self.crear_interfaz_seleccion()
            
        except Exception as e:
            print(f"Error en volver_menu: {e}")
            try:
                self.crear_interfaz_seleccion()
            except:
                pass
    
    def limpiar_simulacion_anterior(self):
        """
        Limpia todos los datos y widgets de la simulación anterior,
        preparando el sistema para una nueva simulación.
        """
        try:
            self.frames_estudiantes.clear()
            self.etiquetas_recursos.clear()
            
            for frame_name in ['scroll_frame_estudiantes', 'scroll_frame_recursos']:
                if hasattr(self, frame_name):
                    frame = getattr(self, frame_name)
                    try:
                        for widget in frame.winfo_children():
                            widget.destroy()
                    except (tk.TclError, AttributeError):
                        pass
            
            if hasattr(self, 'texto_log'):
                try:
                    self.texto_log.configure(state='normal')
                    self.texto_log.delete(1.0, tk.END)
                    self.texto_log.configure(state='disabled')
                except (tk.TclError, AttributeError):
                    pass
            
            try:
                self.sistema.recursos.clear()
                self.sistema.estudiantes.clear()
                if hasattr(self.sistema, 'cola_espera'):
                    self.sistema.cola_espera.clear()
            except:
                pass
                
        except Exception as e:
            print(f"Error en limpiar_simulacion_anterior: {e}")
    
    def inicializar_vista_recursos(self):
        """
        Inicializa la visualización de todos los recursos del sistema,
        agrupándolos por tipo y mostrando su estado actual.
        """
        recursos_por_tipo = {}
        for recurso in self.sistema.recursos:
            tipo = recurso.tipo.value
            if tipo not in recursos_por_tipo:
                recursos_por_tipo[tipo] = []
            recursos_por_tipo[tipo].append(recurso)
        
        row = 0
        for tipo, lista_recursos in recursos_por_tipo.items():
            tipo_frame = tk.Frame(self.scroll_frame_recursos, bg="#345E3C")
            tipo_frame.grid(row=row, column=0, sticky="ew", padx=3, pady=(5, 2))
            
            tipo_display = {
                "Osciloscopio": "🔬 OSCILOSCOPIOS",
                "Generador de Funciones": "⚡ GENERADORES",
                "Licencia de Software": "💿 LICENCIAS",
                "Sala de Experimentación": "🏛️ SALAS"
            }
            
            tk.Label(tipo_frame, text=tipo_display.get(tipo, f"📦 {tipo.upper()}"), font=("Segoe UI", 10, "bold"), bg="#34495E", fg="white", pady=4).pack(fill=tk.X)
            row += 1
            
            for recurso in lista_recursos:
                frame_recurso = tk.Frame(self.scroll_frame_recursos, bg="white", relief="solid", borderwidth=1)
                frame_recurso.grid(row=row, column=0, sticky="ew", padx=3, pady=2)
                
                tk.Label(frame_recurso, text=f"🔧 {recurso.tipo.value[:4]}-{recurso.id}", font=("Segoe UI", 9), bg="white", fg="#2C3E50").pack(side=tk.LEFT, padx=8, pady=4)
                
                etiqueta_estado = tk.Label(frame_recurso, text="✅ Libre", font=("Segoe UI", 9, "bold"), bg="#27AE60", fg="white", padx=6, pady=3)
                etiqueta_estado.pack(side=tk.RIGHT, padx=8, pady=4)
                
                self.etiquetas_recursos[recurso] = etiqueta_estado
                row += 1
        
        self.scroll_frame_recursos.grid_columnconfigure(0, weight=1)
    
    def actualizar_estudiante(self, estudiante):
        """
        Actualiza la visualización de un estudiante específico en la interfaz,
        creando su frame si no existe o actualizando su información.
        """
        if not hasattr(self, 'scroll_frame_estudiantes'):
            return
        
        def _actualizar():
            try:
                if estudiante.id not in self.frames_estudiantes:
                    self._crear_frame_estudiante(estudiante)
                
                if estudiante.id in self.frames_estudiantes:
                    self._actualizar_info_estudiante(estudiante)
                    
            except Exception:
                pass
        
        self.safe_thread_execute(_actualizar)
    
    def _crear_frame_estudiante(self, estudiante):
        """
        Crea el frame visual para mostrar la información de un estudiante,
        incluyendo su estado, recursos y tiempos de espera.
        """
        num_estudiantes = len(self.frames_estudiantes)
        col = num_estudiantes % 2
        row = num_estudiantes // 2
        
        frame = tk.Frame(self.scroll_frame_estudiantes, bg="white", relief="solid", borderwidth=1, width=250)
        frame.grid(row=row, column=col, padx=3, pady=3, sticky="ew")
        
        if not hasattr(self, '_grid_configurado'):
            self.scroll_frame_estudiantes.grid_columnconfigure(0, weight=1)
            self.scroll_frame_estudiantes.grid_columnconfigure(1, weight=1)
            self._grid_configurado = True
        
        header = tk.Frame(frame, bg="#3498DB", height=25)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        nombre_lbl = tk.Label(header, text=f"👨‍🎓 {estudiante.nombre}", font=("Segoe UI", 9, "bold"), bg="#3498DB", fg="white")
        nombre_lbl.pack(side=tk.LEFT, padx=5, pady=2)
        
        tiempo_lbl = tk.Label(header, text="⏱️ 0.0s", font=("Segoe UI", 8), bg="#3498DB", fg="white")
        tiempo_lbl.pack(side=tk.RIGHT, padx=5, pady=2)
        
        contenido = tk.Frame(frame, bg="white")
        contenido.pack(fill=tk.X, padx=5, pady=5)
        
        estado_lbl = tk.Label(contenido, text=f"📊 {estudiante.estado.name}", font=("Segoe UI", 8, "bold"), bg="white", fg="#2C3E50")
        estado_lbl.pack(fill=tk.X, pady=(0, 2))
        
        recursos_lbl = tk.Label(contenido, text="🔧 Recursos: Ninguno", font=("Segoe UI", 7), bg="white", fg="#27AE60", wraplength=180, justify=tk.LEFT)
        recursos_lbl.pack(fill=tk.X, pady=1)
        
        necesarios_lbl = tk.Label(contenido, text="🎯 Necesita: Ninguno", font=("Segoe UI", 7), bg="white", fg="#E74C3C", wraplength=180, justify=tk.LEFT)
        necesarios_lbl.pack(fill=tk.X, pady=1)
        
        self.frames_estudiantes[estudiante.id] = {
            'frame': frame, 'header': header, 'estado': estado_lbl,
            'recursos': recursos_lbl, 'necesarios': necesarios_lbl, 'tiempo': tiempo_lbl
        }
    
    def _actualizar_info_estudiante(self, estudiante):
        """
        Actualiza la información visual de un estudiante específico,
        incluyendo estado, recursos obtenidos y necesarios.
        """
        widgets = self.frames_estudiantes[estudiante.id]
        
        try:
            colores_header = {
                Estado.PENSANDO: "#95A5A6", Estado.ESPERANDO: "#F39C12",
                Estado.TRABAJANDO: "#27AE60", Estado.FINALIZADO: "#3498DB"
            }
            
            widgets['estado'].configure(text=f"📊 {estudiante.estado.name}")
            color_header = colores_header.get(estudiante.estado, "#3498DB")
            widgets['header'].configure(bg=color_header)
            
            for widget in widgets['header'].winfo_children():
                if isinstance(widget, tk.Label):
                    widget.configure(bg=color_header)
            
            if estudiante.recursos_obtenidos:
                recursos_texto = ", ".join([f"{r.tipo.value}-{r.id}" for r in estudiante.recursos_obtenidos])
                widgets['recursos'].configure(text=f"🔧 Recursos: {recursos_texto}")
            else:
                widgets['recursos'].configure(text="🔧 Recursos: Ninguno")
            
            if estudiante.recursos_necesarios:
                necesarios_texto = ", ".join([f"{r.tipo.value}-{r.id}" for r in estudiante.recursos_necesarios])
                widgets['necesarios'].configure(text=f"🎯 Necesita: {necesarios_texto}")
            else:
                widgets['necesarios'].configure(text="🎯 Necesita: Ninguno")
            
            widgets['tiempo'].configure(text=f"⏱️ {estudiante.tiempo_espera:.1f}s")
            
        except tk.TclError:
            if estudiante.id in self.frames_estudiantes:
                del self.frames_estudiantes[estudiante.id]
    
    def actualizar_recursos(self, recursos):
        """
        Actualiza la visualización del estado de todos los recursos,
        mostrando si están libres u ocupados por algún estudiante.
        """
        def _actualizar():
            try:
                for recurso in recursos:
                    if recurso in self.etiquetas_recursos:
                        etiqueta = self.etiquetas_recursos[recurso]
                        if recurso.en_uso:
                            etiqueta.configure(text=f"🔒 Est-{recurso.estudiante_id}", bg="#E74C3C", fg="white")
                        else:
                            etiqueta.configure(text="✅ Libre", bg="#27AE60", fg="white")
            except (tk.TclError, Exception):
                pass
        
        self.safe_thread_execute(_actualizar)
    
    def actualizar_tiempos(self):
        """
        Actualiza periódicamente los tiempos de espera mostrados en la interfaz
        para todos los estudiantes activos en la simulación.
        """
        if hasattr(self, 'scroll_frame_estudiantes') and self.simulacion_activa:
            try:
                for estudiante in self.sistema.estudiantes:
                    if estudiante.id in self.frames_estudiantes:
                        widgets = self.frames_estudiantes[estudiante.id]
                        widgets['tiempo'].configure(text=f"⏱️ {estudiante.tiempo_espera:.1f}s")
            except:
                pass
            
            self.root.after(100, self.actualizar_tiempos)
    
    def agregar_log(self, mensaje):
        """
        Agrega un mensaje de log al área de texto de eventos,
        manteniendo un scroll automático hacia los mensajes más recientes.
        """
        if hasattr(self, 'texto_log'):
            try:
                if self.texto_log.winfo_exists():
                    self.texto_log.configure(state='normal')
                    self.texto_log.insert(tk.END, mensaje + '\n')
                    self.texto_log.configure(state='disabled')
                    self.texto_log.see(tk.END)
            except:
                pass
    
    def cerrar_aplicacion(self):
        """
        Cierra la aplicación correctamente, finalizando todos los hilos
        y liberando recursos antes de terminar el programa.
        """
        try:
            self.simulacion_activa = False
            
            if hasattr(self, 'sistema'):
                self.sistema.finalizar()
            
            self.root.quit()
            self.root.destroy()
            
            import sys
            import os
            
            import time
            time.sleep(0.2)
            
            import threading
            if len(threading.enumerate()) > 1:
                print("Forzando cierre del programa...")
                os._exit(0)
                
        except Exception as e:
            print(f"Error al cerrar: {e}")
            import os
            os._exit(0)
    
    def finalizar(self):
        """
        Finaliza todos los hilos activos y limpia los recursos del sistema,
        forzando la liberación de locks y terminación de procesos pendientes.
        """
        try:
            for recurso in self.recursos:
                try:
                    if recurso.en_uso:
                        recurso.en_uso = False
                        recurso.estudiante_id = None
                        try:
                            recurso.lock.release()
                        except:
                            pass
                except:
                    pass
            
            for estudiante in self.estudiantes:
                if estudiante.is_alive():
                    estudiante.join(timeout=1.0)
                    
                    if estudiante.is_alive():
                        print(f"Forzando terminación de {estudiante.nombre}")
            
            self.estudiantes.clear()
            self.recursos.clear()
            
        except Exception as e:
            print(f"Error en finalizar: {e}")