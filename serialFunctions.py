import serial
import time
from serial.tools import list_ports

ser = None

def open_serial(port="/dev/ttyUSB0", baudrate=9600, timeout=1):
    global ser
    try:
        ser = serial.Serial(port, baudrate, timeout=timeout)
        return f"Connected to {port} @ {baudrate}"
        time.sleep(2)
    except serial.SerialException as e:
        return f"ERROR to open {port}: {e}"


def close_serial():
    if ser and ser.is_open:
        ser.close()

def getFilteredPorts() -> list:
    """Devuelve lista de puertos serie filtrados: USB, ACM, CDC"""
    try:
        # Obtener todos los puertos disponibles
        ports = list_ports.comports()
        # Filtrar solo los puertos que contengan "USB", "ACM" o "CDC"
        filtered_ports = [
            (p.device, p.device)
            for p in ports
            if "USB" in p.device or "ACM" in p.device or "AMA" in p.device
            or "CDC" in (p.description or "").upper()
        ]
        # Si no se encuentran puertos, devolver "None"
        return filtered_ports or [("None", "None")]
    except Exception as e:
        return f"excp err at get ports: {str(e)}"

def serialSendCmd(command: str):
    """Envía un comando al dispositivo"""
    try:
        ser.reset_input_buffer()  # Limpia datos anteriores
        ser.write((command + '\n').encode())

        time.sleep(0.2)  # Espera pequeña para que comience la respuesta
        
    except Exception as e:
        return f"excp err at sending: {str(e)}"


def serialResponse() -> str:
    """Recibe la respuesta del dispositivo hasta '\f' o hasta un timeout"""
    try:
        response_lines = []
        last_read_time = time.time()
        timeout_seconds = 2.0  # máximo tiempo sin recibir datos

        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode(errors="ignore").strip()

                # Verificamos fin de mensaje
                if '\f' in line:
                    clean_line = line.replace('\f', '').strip()
                    if clean_line:
                        response_lines.append(clean_line)
                    break

                response_lines.append(line)
                last_read_time = time.time()

            else:
                # Dormir un poco para no sobrecargar CPU
                time.sleep(0.01)

                # Si pasó demasiado tiempo sin recibir nada
                if time.time() - last_read_time > timeout_seconds:
                    break

        return "\n".join(response_lines)

    except Exception as e:
        return f"Error at receiving: {str(e)}"


def serialFilter(filt,line) -> str:
    """Filtra informacion dependiendo la respuesta"""
    filt=str(filt)
    line=str(line)
    if line.startswith(filt):
        return line[len(filt),len(line)]
    else:
        return ""

def serialInit() -> str:
    """Envía el comando 'get' para que el dispositivo inicie el envío de datos"""
    try:
        command = "get"
        serialSendCmd(command)
        response = serialResponse()
        
        return response
    except Exception as e:
        return f"excp err en serialInit: {str(e)}"

def serialLoop(soft=False, hard=False) -> str:
    try:
        return serialSendCmd("LOOP")
    except Exception as e:
        return f"Error at serialLoop: {e}"

def serialStop() -> str:
    pass

def serialMeasures(N: int) -> str:
    pass

def serialDelay(ms: int) -> str:
    pass
