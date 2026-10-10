from config.logger import Logger

class SistemaConfig:            # Singleton con la configuración global
    _inst = None
    def __new__(cls):
        if cls._inst is None: 
            cls._inst  = super().__new__(cls) 
            cls._inst.nombre  = "Sistema de Gestión Cursos y Estudiantes"  
            cls._inst.version = "3.0"
            cls._inst.empresa = "ISTP Argentina"
            cls._inst.autor ="Tello Luis - Castro Raquel"
            Logger().info(f"Sistema Inicado :{cls._inst.nombre} Version :{cls._inst.version} Empresa :{cls._inst.empresa} Autor :{cls._inst.autor}")
        return cls._inst     
