import threading
import time
import random
import queue
import logging
from enums import TipoRecurso
from recurso import Recurso
from estudiante import Estudiante

class SistemaGestionRecursos:
    def __init__(self):
        """
        Inicializa el sistema de gestión de recursos del laboratorio,
        configurando las listas de recursos, estudiantes y colas de espera.
        """
        self.recursos = []
        self.estudiantes = []
        self.cola_espera = {}
        self.lock_sistema = threading.Lock()
        self.interfaz = None
        self.inanition_solution_enabled = False  # ← AGREGA ESTA LÍNEA
    
    def inicializar_recursos(self):
        """
        Crea e inicializa todos los recursos disponibles en el laboratorio,
        configurando un recurso de cada tipo y sus respectivas colas de espera.
        """
        for i in range(1):
            self.recursos.append(Recurso(i+1, TipoRecurso.OSCILOSCOPIO))
        for i in range(1):
            self.recursos.append(Recurso(i+1, TipoRecurso.GENERADOR))
        for i in range(1):
            self.recursos.append(Recurso(i+1, TipoRecurso.LICENCIA_SOFTWARE))
        for i in range(1):
            self.recursos.append(Recurso(i+1, TipoRecurso.SALA))
        
        for recurso in self.recursos:
            self.cola_espera[recurso] = queue.Queue()
    
    def obtener_recurso(self, estudiante, recurso):
        """
        Intenta que un estudiante obtenga un recurso específico del sistema,
        implementando lógicas de prioridad y condiciones de carrera problemáticas.
        """
        if self.inanition_solution_enabled: # Obtiene el recurso con la solución de inanición si esta habilitada
            return self.get_resource_with_inanition_solution(estudiante, recurso)
        else:
            if not recurso.en_uso:
                cola_actual = list(self.cola_espera[recurso].queue)
                
                for est_en_espera in cola_actual:
                    if est_en_espera.id < estudiante.id:
                        self.cola_espera[recurso].put(estudiante)
                        logging.info(f"{estudiante.nombre} debe esperar - hay estudiantes prioritarios")
                        return False
                    
                time.sleep(0.01)
                
                if recurso.lock.acquire(blocking=False):
                    recurso.en_uso = True
                    recurso.estudiante_id = estudiante.id
                    logging.info(f"{estudiante.nombre} obtuvo {recurso}")
                    self.actualizar_interfaz()
                    return True
                else:
                    return False
            else:
                if estudiante not in list(self.cola_espera[recurso].queue):
                    self.cola_espera[recurso].put(estudiante)
                    logging.info(f"{estudiante.nombre} agregado a cola de espera para {recurso}")
                return False
    
    def liberar_recurso(self, estudiante, recurso):
        """
        Libera un recurso que estaba siendo utilizado por un estudiante,
        notificando a estudiantes en espera y actualizando la interfaz.
        """
        if recurso.estudiante_id == estudiante.id:
            recurso.en_uso = False
            recurso.estudiante_id = None
            logging.info(f"{estudiante.nombre} liberó {recurso}")
            
            if not self.inanition_solution_enabled: #Se evita el interbloqueo si la solución de inanición está habilitada
                if not self.cola_espera[recurso].empty():   #Esto puede ocasionar un interbloqueo porque elimina el primer estudiante de la cola(El siguiente en obtener el recurso) sin embargo, no se le asigna el recurso inmediatamente, esto puede ocasionar que nunca se le asigne el recurso 
                    estudiante_esperando = self.cola_espera[recurso].get()
                    logging.info(f"{estudiante_esperando.nombre} podría obtener {recurso} ahora")
            recurso.lock.release()
            self.actualizar_interfaz()
    
    def iniciar_simulacion(self, num_estudiantes):
        """
        Inicia la simulación con un número determinado de estudiantes,
        creando estudiantes con recursos específicos que provocan interbloqueo.
        """
        estudiante1 = Estudiante(1, self, [self.recursos[0], self.recursos[3]], self.interfaz, tiempo_trabajo=10)
        self.estudiantes.append(estudiante1)
        
        estudiante2 = Estudiante(2, self, [self.recursos[3], self.recursos[0]], self.interfaz, tiempo_trabajo=10)
        self.estudiantes.append(estudiante2)
        
        for i in range(3, num_estudiantes+1):
            num_recursos = 2
            recursos_necesarios = random.sample(self.recursos, num_recursos)
            tiempo_trabajo = random.randint(5, 8)
            estudiante = Estudiante(i, self, recursos_necesarios, self.interfaz, tiempo_trabajo)
            self.estudiantes.append(estudiante)
        
        for estudiante in self.estudiantes:
            estudiante.start()
            time.sleep(0.1)
    
    def configurar_interfaz(self, interfaz):
        """
        Establece la conexión entre el sistema y la interfaz gráfica,
        permitiendo la actualización visual del estado de los recursos.
        """
        self.interfaz = interfaz
    
    def actualizar_interfaz(self):
        """
        Actualiza la interfaz gráfica con el estado actual de todos los recursos,
        mostrando cuáles están libres u ocupados por estudiantes.
        """
        if self.interfaz:
            self.interfaz.actualizar_recursos(self.recursos)
    
    def finalizar(self):
        """
        Finaliza todos los hilos activos y limpia el estado de los recursos,
        asegurando una terminación correcta del sistema.
        """
        for estudiante in self.estudiantes:
            if estudiante.is_alive():
                estudiante.join(timeout=0.1)
        
        for recurso in self.recursos:
            recurso.en_uso = False
            recurso.estudiante_id = None
    
    def iniciar_simulacion_interbloqueo(self, num_estudiantes=4):
        """
        Inicia una simulación específicamente diseñada para crear interbloqueo,
        configurando estudiantes que solicitan recursos en órdenes problemáticos.
        """
        logging.info("Iniciando simulación de INTERBLOQUEO")
        
        estudiante1 = Estudiante(1, self, [self.recursos[0], self.recursos[3]], self.interfaz, tiempo_trabajo=10)
        self.estudiantes.append(estudiante1)
        
        estudiante2 = Estudiante(2, self, [self.recursos[3], self.recursos[0]], self.interfaz, tiempo_trabajo=10)
        self.estudiantes.append(estudiante2)
        
        estudiante3 = Estudiante(3, self, [self.recursos[1], self.recursos[2]], self.interfaz, tiempo_trabajo=8)
        self.estudiantes.append(estudiante3)
        
        estudiante4 = Estudiante(4, self, [self.recursos[2], self.recursos[1]], self.interfaz, tiempo_trabajo=8)
        self.estudiantes.append(estudiante4)
        
        for i, estudiante in enumerate(self.estudiantes):
            estudiante.start()
            time.sleep(0.2)
    
    def iniciar_simulacion_inanicion(self, solution_enabled, num_estudiantes=6):
        """
        Inicia una simulación diseñada para crear inanición de recursos,
        configurando estudiantes con diferentes prioridades y tiempos de trabajo.
        """
        logging.info("Iniciando simulación de INANICIÓN")
        self.inanition_solution_enabled = solution_enabled  # Habilita o deshabilita la solución de inanición
        for i in range(1, 4):
            recursos_necesarios = [self.recursos[0], self.recursos[1]]
            tiempo_trabajo = 15
            estudiante = Estudiante(i, self, recursos_necesarios, self.interfaz, tiempo_trabajo)
            self.estudiantes.append(estudiante)
        
        for i in range(4, num_estudiantes + 1):
            recursos_necesarios = [self.recursos[0]]
            tiempo_trabajo = 3
            estudiante = Estudiante(i, self, recursos_necesarios, self.interfaz, tiempo_trabajo)
            self.estudiantes.append(estudiante)
        
        for estudiante in self.estudiantes:
            if self.inanition_solution_enabled: # Habilita la solución de inanición si está configurada
                estudiante.inanition_solution_is_enabled(True)
            estudiante.start()
            time.sleep(0.1)
    
    def iniciar_simulacion_condiciones_carrera(self, num_estudiantes=5):
        """
        Inicia una simulación diseñada para crear condiciones de carrera,
        configurando múltiples estudiantes compitiendo simultáneamente por recursos.
        """
        logging.info("Iniciando simulación de CONDICIONES DE CARRERA")
        
        for i in range(1, num_estudiantes + 1):
            recursos_necesarios = [self.recursos[0], self.recursos[1]]
            tiempo_trabajo = random.randint(2, 5)
            estudiante = Estudiante(i, self, recursos_necesarios, self.interfaz, tiempo_trabajo)
            self.estudiantes.append(estudiante)
        
        for estudiante in self.estudiantes:
            estudiante.start()
    
    def get_resource_with_inanition_solution(self, estudiante, recurso):
        """
        Intenta que un estudiante obtenga un recurso utilizando una solución de inanición, esta solución consta de lo siguiente:
        - Si el estudiante no está en la cola de espera de un recurso, agrega el estudiante a la cola.
        - Solo el primer estudiante en la cola puede intentar obtener el recurso(Evidentemente).
        - Una vez que el estudiante obtiene el recurso(adquiere), se marca el recurso como 'en uso', es decir le pone un candado 
        que impide que otros estudiantes adquieran el recurso en el mismo instante y actualiza el estado del recurso.
        Args:
            estudiante (Estudiante): el estudiante que intenta obtener el recurso
            recurso (Recurso): el recurso que se intenta obtener

        Returns:
            Boolean: True si el estudiante obtiene el recurso satisfactoriamente, False en caso contrario.
        """
        
        # Verifica si el estudiante ya esta en la cola, si no lo esta, entonces lo añade en la ultima posición.
        if estudiante not in list(self.cola_espera[recurso].queue):
            self.cola_espera[recurso].put(estudiante)
            logging.info(f"{estudiante.nombre} agregado a cola de espera para {recurso}")

        # Solo el primero en la cola puede intentar obtener el recurso
        if self.cola_espera[recurso].queue[0] != estudiante:
            return False

        if not recurso.en_uso and recurso.lock.acquire(blocking=False):
            recurso.en_uso = True
            recurso.estudiante_id = estudiante.id
            logging.info(f"{estudiante.nombre} obtuvo {recurso}")
            self.cola_espera[recurso].get()  # Sale de la cola
            self.actualizar_interfaz()
            return True
        else:
            return False