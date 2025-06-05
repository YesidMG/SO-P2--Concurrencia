from enum import Enum, auto

class Estado(Enum):
    """
    Enumeración que define los diferentes estados en los que puede encontrarse
    un estudiante durante la simulación del sistema de gestión de recursos.
    """
    PENSANDO = auto()
    ESPERANDO = auto()
    TRABAJANDO = auto()
    FINALIZADO = auto()

class TipoRecurso(Enum):
    """
    Enumeración que define los diferentes tipos de recursos disponibles
    en el laboratorio para ser utilizados por los estudiantes.
    """
    OSCILOSCOPIO = "Osciloscopio"
    GENERADOR = "Generador de Funciones"
    LICENCIA_SOFTWARE = "Licencia de Software"
    SALA = "Sala de Experimentación"