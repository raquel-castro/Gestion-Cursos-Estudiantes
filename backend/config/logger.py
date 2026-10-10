import datetime


class Logger:

    _instancia = None

    def __new__(cls):

        if cls._instancia is None:

            cls._instancia = super().__new__(cls)
            cls._instancia._logs = []

        return cls._instancia


    def _registrar(self, nivel, mensaje):

        hora = datetime.datetime.now().strftime("%H:%M:%S")

        entrada = {
            "hora": hora,
            "nivel": nivel,
            "msg": mensaje
        }

        self._logs.append(entrada)


    def info(self, msg):

        self._registrar("INFO", msg)


    def warning(self, msg):

        self._registrar("WARNING", msg)


    def error(self, msg):

        self._registrar("ERROR", msg)


    def mostrar_logs(self):

        print(
            f"\n=== HISTORIAL DEL SISTEMA "
            f"({len(self._logs)} eventos) ==="
        )

        for log in self._logs:

            print(
                f"  [{log['hora']}] "
                f"{log['nivel']:7} | "
                f"{log['msg']}"
            )


    def obtener_logs(self):

        return self._logs.copy()


    def limpiar(self):

        self._logs.clear()

        print("OK Historial de logs limpiado.")