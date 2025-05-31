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
        self.inanition_solution_enabled = False
        self.usar_semaforo_carrera = False  
    
    def run(self):
        """
        Ejecuta el ciclo de vida completo del estudiante: solicitar recursos,
        trabajar con ellos y liberarlos al finalizar, manejando errores y limpieza.
        """
        try:
            if self.inanition_solution_enabled:
                self.run_round_robin_inanition_solution()
            elif getattr(self, 'usar_semaforo_carrera', False):
                
                waiting_begin = time.time()
                while True:
                    acquired = self.sistema.semaforo_carrera.acquire(blocking=False)
                    if acquired:
                        break
                    time.sleep(0.1)
                    self.tiempo_espera += 0.1
                    self.actualizar_interfaz()
                    
                self._ejecutar_trabajo()
                self.sistema.semaforo_carrera.release()
            else:
                self._ejecutar_trabajo()
        except Exception as e:
            logging.error(f"Error en {self.nombre}: {e}")
        finally:
            for recurso in self.recursos_obtenidos:
                try:
                    self.sistema.liberar_recurso(self, recurso)
                except:
                    pass

    def _ejecutar_trabajo(self):
        """
        Ejecuta el trabajo del estudiante, solicitando recursos, trabajando con ellos y liberándolos al finalizar.
        """
        self.estado = Estado.ESPERANDO
        self.actualizar_interfaz()
        logging.info(f"{self.nombre} comienza a solicitar recursos: {[str(r) for r in self.recursos_necesarios]}")
        waiting_begin = time.time()
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
                self.actualizar_interfaz()
            self.recursos_obtenidos.append(recurso)
            self.actualizar_interfaz()
            time.sleep(0.2)
        waiting_end = time.time()
        waiting_total_time = waiting_end - waiting_begin

        self.estado = Estado.TRABAJANDO
        self.actualizar_interfaz()
        logging.info(f"{self.nombre} comienza a trabajar con los recursos obtenidos")
        time.sleep(self.tiempo_trabajo)

        for recurso in self.recursos_obtenidos:
            self.sistema.liberar_recurso(self, recurso)

        self.recursos_obtenidos.clear()
        self.estado = Estado.FINALIZADO
        self.actualizar_interfaz()
        logging.info(f"{self.nombre} ha finalizado su trabajo. Tiempo de espera: {waiting_total_time:.2f}s")

    def actualizar_interfaz(self):
        """
        Actualiza la representación visual del estudiante en la interfaz gráfica,
        mostrando su estado actual y recursos obtenidos.
        """
        if self.interfaz:
            self.interfaz.actualizar_estudiante(self)
    
    def inanition_solution_is_enabled(self, enabled):
        """
        Habilita o deshabilita la solución de inanición con Round Robin para la asiganción de recursos del estudiante.
        Args:
            enabled (boolean): True si se habilita la solución de inanición, False si se deshabilita.
        """
        logging.info(f"-----------Iniciando solución de inanición con Round Robin para {self.nombre}---------------")
        self.inanition_solution_enabled = enabled
        
    def run_round_robin_inanition_solution(self):
        """
        Ejecuta el ciclo de vida completo del estudiante usando el metodo de Round Robin:
        en el cual solicita recursos, ingresa a colas de espera a esos recursos, trabaja por quantums 
        y una vez completa un quantum de trabajo libera los recursos que tiene asignado temporalmente
        para que otro estudiante los use si aun no termina su trabajo.
        """
        quantum = 2  # duración del quantum(tiempo de trabajo cada turno)
        self.start_waiting()
        waiting_begin = time.time()
        self.waiting_resources_first_time()
        waiting_end = time.time()
        waiting_total_time = waiting_end - waiting_begin
        self.execute_work_round_robin(quantum)
        self.finish_work(waiting_total_time)

    def start_waiting(self):
        """
        Coloca al estudiante en estado de espera y actualiza esta información en la interfaz.
        """
        self.estado = Estado.ESPERANDO
        self.actualizar_interfaz()
        logging.info(f"{self.nombre} comienza a solicitar recursos: {[str(r) for r in self.recursos_necesarios]}")

    def waiting_resources_first_time(self):
        """
        Solicita por primera vez todos los recursos necesarios para iniciar el trabajo. Si un recurso no esta disponible 
        ingresa en la cola de espera del recurso y espera hasta que este se libere y sea su turno de usarlo.
        """
        for recurso in self.recursos_necesarios:
            if hasattr(self.interfaz, 'simulacion_activa') and not self.interfaz.simulacion_activa:
                logging.info(f"{self.nombre} terminando por cierre de aplicación")
                return

            while not self.sistema.obtener_recurso(self, recurso):
                self.waiting_resources()

            self.recursos_obtenidos.append(recurso)
            self.actualizar_interfaz()
            time.sleep(0.2) #Duerme un poco para simular el tiempo de espera al solicitar recursos y no recargar el programa con actualizaciones visuales
    
    def waiting_resources(self):
        """
        Coloca al estudiante en espera si no puede obtener un recurso.
        """
        if hasattr(self.interfaz, 'simulacion_activa') and not self.interfaz.simulacion_activa:
            logging.info(f"{self.nombre} terminando por cierre de aplicación")
            return
        time.sleep(0.1)
        self.tiempo_espera += 0.1

    def execute_work_round_robin(self, quantum):
        """
        Ejecuta el trabajo del estudiante durante un quantum de tiempo, luego libera 
        los recursos asignados si aun no ha terminado su trabajo para que otro estudiante 
        pueda acceder a ellos y utilizarlos.
        Args:
            quantum (number): Duración del turno de trabajo del estudiante, en el cual utiliza sus recursos asignados.
        """
        tiempo_restante = self.tiempo_trabajo
        while tiempo_restante > 0:
            self.estado = Estado.TRABAJANDO
            self.actualizar_interfaz()
            logging.info(f"{self.nombre} trabajando con recursos obtenidos durante un quantum")
            trabajo = min(quantum, tiempo_restante)
            time.sleep(trabajo)
            tiempo_restante -= trabajo

            # Si no terminó su trabajo, libera los recursos y vuelve a esperar su turno
            if tiempo_restante > 0:
                self.release_all_resources()
                self.estado = Estado.ESPERANDO
                self.actualizar_interfaz()
                self.obtaining_resources_again()
                self.actualizar_interfaz()
                time.sleep(0.2)

    def release_all_resources(self):
        """
        Libera todos los recursos actualmente obtenidos por el estudiante para que otro estudiante los utilice.
        """
        for recurso in self.recursos_obtenidos:
            self.sistema.liberar_recurso(self, recurso)
        self.recursos_obtenidos.clear()

    def obtaining_resources_again(self):
        """
        Solicita nuevamente todos los recursos necesarios para continuar el trabajo. Si un recurso no esta disponible 
        ingresa en la cola de espera del recurso y espera hasta que este se libere y sea su turno de usarlo.
        """
        for recurso in self.recursos_necesarios:
            while not self.sistema.obtener_recurso(self, recurso):
                self.waiting_resources()
            if recurso not in self.recursos_obtenidos:
                self.recursos_obtenidos.append(recurso)

    def finish_work(self, waiting_total_time):
        """
        Libera los recursos al finalizar el trabajo y actualiza el estado final del estudiante.
        Args:
            waiting_total_time (number): Suma de todos los tiempos de espera del estudiante para obtener los recursos que necesita hasta el momento actual.
        """
        for recurso in self.recursos_obtenidos:
            self.sistema.liberar_recurso(self, recurso)
        self.recursos_obtenidos.clear()
        self.estado = Estado.FINALIZADO
        self.actualizar_interfaz()
        logging.info(f"{self.nombre} ha finalizado su trabajo. Tiempo de espera: {waiting_total_time:.2f}s")
    
    def __str__(self):
        """
        Retorna una representación en cadena del estudiante,
        mostrando su nombre para identificación en logs y depuración.
        """
        return self.nombre

    def iniciar_simulacion_interbloqueo_solucionada(self, num_estudiantes=4):
        """
        Simula el problema de interbloqueo pero forzando a todos los estudiantes
        a solicitar los recursos SIEMPRE en el mismo orden, evitando el deadlock.
        """
        logging.info("Iniciando simulación de INTERBLOQUEO (SOLUCIONADO: orden en adquisición de locks)")
        self.estudiantes.clear()
        recursos_ordenados = sorted(self.recursos, key=lambda r: (r.tipo.value, r.id))
        for i in range(1, num_estudiantes + 1):
            estudiante = Estudiante(i, self, recursos_ordenados[:2], self.interfaz, tiempo_trabajo=8)
            self.estudiantes.append(estudiante)
        for estudiante in self.estudiantes:
            estudiante.start()