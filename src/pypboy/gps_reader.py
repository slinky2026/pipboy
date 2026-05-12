import time

try:
    import serial
except ImportError:
    serial = None


class GPSReader:
    def __init__(self, port="/dev/ttyACM0", baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.lat = None
        self.lon = None
        self.last_update = 0

    def convert_to_decimal(self, raw_value, direction):
        if not raw_value:
            return None

        value = float(raw_value)
        degrees = int(value // 100)
        minutes = value - (degrees * 100)

        decimal = degrees + (minutes / 60)

        if direction in ["S", "W"]:
            decimal *= -1

        return decimal

    def update(self):
        # If pyserial is missing or no GPS is attached, fail safely
        if serial is None:
            print("GPS unavailable: pyserial not installed")
            return self.lat, self.lon

        try:
            with serial.Serial(self.port, self.baudrate, timeout=1) as gps:
                start_time = time.time()

                while time.time() - start_time < 2:
                    line = gps.readline().decode("ascii", errors="ignore").strip()

                    if line.startswith("$GPRMC") or line.startswith("$GNRMC"):
                        parts = line.split(",")

                        if len(parts) > 6 and parts[2] == "A":
                            lat = self.convert_to_decimal(parts[3], parts[4])
                            lon = self.convert_to_decimal(parts[5], parts[6])

                            if lat is not None and lon is not None:
                                self.lat = lat
                                self.lon = lon
                                self.last_update = time.time()
                                return self.lat, self.lon

        except Exception as e:
            print("GPS unavailable:", repr(e))

        return self.lat, self.lon