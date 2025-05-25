import threading
import time
import logging
from enums import Estado

class Estudiante(threading.Thread):
    def __init__(self, id, sistema, recursos_necesarios, interfaz, tiempo_trabajo=5):
        """
        Inicializa un estudiante como hilo de ejecución que solicita recursos del sistema,
        configurando su identificación, recursos necesarios y tiempo de trabajo.
        """
        super().__init__(name=f"Estudiante-{id}")
        self.id = id
        self.nombre = f"Estudiante {id}"
        self.sistema = sistema
        self.recursos_necesarios = recursos_necesarios.copy()  
        self.recursos_obtenidos = []  
        self.estado = Estado.PENSANDO
        self.interfaz = interfaz
        self.tiempo_trabajo = tiempo_trabajo  
        self.tiempo_espera = 0  
    
    def run(self):
        """
        Ejecuta el ciclo de vida completo del estudiante: solicitar recursos,
        trabajar con ellos y liberarlos al finalizar, manejando errores y limpieza.
        """
        try:
            self.estado = Estado.ESPERANDO
            self.actualizar_interfaz()
            logging.info(f"{self.nombre} comienza a solicitar recursos: {[str(r) for r in self.recursos_necesarios]}")

            inicio_espera = time.time()
            for recurso in self.recursos_necesarios:
                if hasattr(self.interfaz, 'simulacion_activa') and not self.interfaz.simulacion_activa:
                    logging.info(f"{self.nombre} terminando por cierre de aplicación")
                    return
                    
                while not self.sistema.obtener_recurso(self, recurso):
                    if hasattr(self.interfaz, 'simulacion_activa') and not self.interfaz.simulacion_activa:
                        logging.info(f"{self.nombre} terminando por cierre de aplicación")
                        return
                        
                    time.sleep(0.1)
                    self.tiempo_espera += 0.1
                
                self.recursos_obtenidos.append(recurso)
                self.actualizar_interfaz()
                time.sleep(0.2) 
            
            fin_espera = time.time()
            tiempo_total_espera = fin_espera - inicio_espera

            self.estado = Estado.TRABAJANDO
            self.actualizar_interfaz()
            logging.info(f"{self.nombre} comienza a trabajar con los recursos obtenidos")
            time.sleep(self.tiempo_trabajo)

            for recurso in self.recursos_obtenidos:
                self.sistema.liberar_recurso(self, recurso)
            
            self.recursos_obtenidos.clear()
            self.estado = Estado.FINALIZADO
            self.actualizar_interfaz()
            logging.info(f"{self.nombre} ha finalizado su trabajo. Tiempo de espera: {tiempo_total_espera:.2f}s")
            
        except Exception as e:
            logging.error(f"Error en {self.nombre}: {e}")
        finally:
            for recurso in self.recursos_obtenidos:
                try:
                    self.sistema.liberar_recurso(self, recurso)
                except:
                    pass
    
    def actualizar_interfaz(self):
        """
        Actualiza la representación visual del estudiante en la interfaz gráfica,
        mostrando su estado actual y recursos obtenidos.
        """
        if self.interfaz:
            self.interfaz.actualizar_estudiante(self)
    
    def __str__(self):
        """
        Retorna una representación en cadena del estudiante,
        mostrando su nombre para identificación en logs y depuración.
        """
        return self.nombre