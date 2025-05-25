import threading

class Recurso:
    def __init__(self, id, tipo):
        """
        Inicializa un recurso del laboratorio con identificación única y tipo específico,
        configurando su estado inicial como libre y creando un lock para control de acceso.
        """
        self.id = id
        self.tipo = tipo
        self.en_uso = False
        self.estudiante_id = None
        self.lock = threading.Lock()
    
    def __str__(self):
        """
        Retorna una representación en cadena del recurso mostrando su tipo e identificador,
        utilizada para mostrar información del recurso en la interfaz y logs del sistema.
        """
        return f"{self.tipo.value} {self.id}"