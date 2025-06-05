import tkinter as tk 
import logging
from sistema_gestion_recursos import SistemaGestionRecursos
from interfaz_grafica import InterfazGrafica

class GuiLogHandler(logging.Handler):
    def __init__(self):
        """
        Inicializa el handler personalizado para enviar logs a la interfaz gráfica,
        configurando la conexión inicial sin interfaz asignada.
        """
        super().__init__()
        self.interfaz = None
    
    def set_interfaz(self, interfaz):
        """
        Establece la conexión entre el handler de logging y la interfaz gráfica,
        permitiendo que los logs se muestren en tiempo real en la aplicación.
        """
        self.interfaz = interfaz
        print(f"Handler conectado a interfaz: {interfaz}")
        print(f"¿Tiene método agregar_log? {hasattr(interfaz, 'agregar_log')}")
    
    def emit(self, record):
        """
        Emite un mensaje de log hacia la interfaz gráfica de forma thread-safe,
        utilizando el método after de tkinter para evitar problemas de concurrencia.
        """
        if self.interfaz:
            msg = self.format(record)
            print(f"Enviando log: {msg}")
            try:
                self.interfaz.root.after(0, lambda: self.interfaz.agregar_log(msg))
            except Exception as e:
                print(f"Error al enviar log: {e}")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

gui_handler = GuiLogHandler()
gui_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
))

logger = logging.getLogger()
logger.addHandler(gui_handler)

if __name__ == "__main__":
    def main():
        """
        Función principal que inicializa el sistema de gestión de recursos,
        crea la interfaz gráfica y configura el logging para toda la aplicación.
        """
        sistema = SistemaGestionRecursos()
        sistema.inicializar_recursos()
        
        root = tk.Tk()
        interfaz = InterfazGrafica(root, sistema)
        
        gui_handler.set_interfaz(interfaz)
        
        for module_name in ['sistema_gestion_recursos', 'interfaz_grafica']:
            module_logger = logging.getLogger(module_name)
            module_logger.addHandler(gui_handler)
            module_logger.setLevel(logging.INFO)
        
        logging.info("Sistema iniciado correctamente")
        
        root.mainloop()
    
    main()