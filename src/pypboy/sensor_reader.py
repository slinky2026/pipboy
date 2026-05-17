try:
    import serial
except ImportError:
    serial = None


class SensorReader:
    
    #    HR:79,IR:133075 example format

  
    def __init__(self, port="/dev/ttyUSB0", baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.serial_connection = None

        self.heart_rate = None
        self.ir_value = None

        if serial is None:
            print("pyserial not installed; sensor disabled.")
            return

        try:
            self.serial_connection = serial.Serial(
                self.port,
                self.baudrate,
                timeout=0.1
            )
            print(f"Sensor connected on {self.port}")

        except Exception as e:
            print(f"Sensor unavailable on {self.port}: {e}")
            self.serial_connection = None

    def update(self):
        

        if self.serial_connection is None:
            return self.heart_rate, self.ir_value

        try:
            line = self.serial_connection.readline().decode(
                "utf-8",
                errors="ignore"
            ).strip()

            if not line.startswith("HR:"):
                return self.heart_rate, self.ir_value

            # Example: HR:79,IR:133075
            parts = line.split(",")

            hr_text = parts[0].replace("HR:", "")
            ir_text = parts[1].replace("IR:", "")

            hr = int(hr_text)
            ir = int(ir_text)

            # Ignore zero cos how does that comtribute to HR? it doesnt. dumb.
            if hr > 0:
                self.heart_rate = hr

            self.ir_value = ir

        except Exception as e:
            print(f"Sensor parse failed: {e}")

        return self.heart_rate, self.ir_value