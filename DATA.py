import serial
import csv
import os
from datetime import datetime


# ==================================================
# ARDUINO SETTINGS
# ==================================================

PORT = "COM4"
BAUD = 9600


# ==================================================
# DATASET SETTINGS
# ==================================================

READINGS_PER_CONDITION = 500

CSV_FILE = "sensor_dataset.csv"


# ==================================================
# CONNECT TO ARDUINO
# ==================================================

print("Connecting to Arduino...")

try:
    ser = serial.Serial(PORT, BAUD, timeout=2)

except serial.SerialException as e:
    print()
    print("Could not connect to Arduino.")
    print("Check that:")
    print("1. Arduino is connected.")
    print("2. Correct COM port is selected.")
    print("3. Arduino Serial Monitor is CLOSED.")
    print()
    print("Error:", e)
    input("\nPress Enter to exit...")
    exit()


print("Arduino connected!")
print()


# ==================================================
# CHECK CSV FILE
# ==================================================

file_exists = os.path.exists(CSV_FILE)

try:

    file = open(
        CSV_FILE,
        "a",
        newline=""
    )

except PermissionError:

    print()
    print("ERROR: sensor_dataset.csv is locked!")
    print()
    print("Please:")
    print("1. Close sensor_dataset.csv in Excel.")
    print("2. Close any other program using the CSV.")
    print("3. Run this Python program again.")
    print()

    ser.close()

    input("Press Enter to exit...")
    exit()


# ==================================================
# CREATE CSV WRITER
# ==================================================

writer = csv.writer(file)


# ==================================================
# WRITE HEADER ONLY IF FILE IS EMPTY
# ==================================================

if not file_exists or os.path.getsize(CSV_FILE) == 0:

    writer.writerow([
        "PC_Timestamp",
        "Arduino_Time_ms",
        "Condition",
        "Temperature_C",
        "Accel_X",
        "Accel_Y",
        "Accel_Z"
    ])

    file.flush()


print("CSV file ready:")
print(CSV_FILE)
print()


# ==================================================
# CONDITION LOOP
# ==================================================

try:

    while True:

        print("----------------------------------------")

        condition = input(
            "Enter condition (or type STOP): "
        ).strip()


        # Stop program
        if condition.upper() == "STOP":
            break


        # Empty condition
        if condition == "":
            print("Please enter a condition.")
            continue


        print()
        print("Condition:", condition)
        print(
            "Collecting",
            READINGS_PER_CONDITION,
            "readings..."
        )
        print()


        count = 0


        # ==================================================
        # COLLECT SENSOR READINGS
        # ==================================================

        while count < READINGS_PER_CONDITION:

            # Read Arduino line
            line = ser.readline().decode(
                "utf-8",
                errors="ignore"
            ).strip()


            # Ignore empty lines
            if not line:
                continue


            # Ignore Arduino messages
            if line.startswith("Starting"):
                continue

            if line.startswith("MPU6050"):
                continue

            if line.startswith("-"):
                continue

            if line.startswith("Timestamp_ms"):
                continue


            # ==================================================
            # SPLIT TAB-SEPARATED DATA
            # ==================================================

            parts = line.split("\t")


            # Arduino should send:
            #
            # Timestamp
            # Temperature
            # Accel_X
            # Accel_Y
            # Accel_Z

            if len(parts) != 5:
                continue


            # ==================================================
            # CONVERT DATA TO NUMBERS
            # ==================================================

            try:

                arduino_time = int(parts[0])

                temperature = float(parts[1])

                accel_x = float(parts[2])

                accel_y = float(parts[3])

                accel_z = float(parts[4])

            except ValueError:

                continue


            # ==================================================
            # PC TIMESTAMP
            # ==================================================

            pc_timestamp = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S.%f"
            )[:-3]


            # ==================================================
            # WRITE DATA TO CSV
            # ==================================================

            try:

                writer.writerow([
                    pc_timestamp,
                    arduino_time,
                    condition,
                    temperature,
                    accel_x,
                    accel_y,
                    accel_z
                ])

                file.flush()

            except PermissionError:

                print()
                print("ERROR: Excel has locked the CSV file!")
                print()
                print("Close sensor_dataset.csv in Excel.")
                print("Then restart the Python program.")
                print()

                raise


            # ==================================================
            # UPDATE COUNTER
            # ==================================================

            count += 1


            # ==================================================
            # SHOW PROGRESS
            # ==================================================

            print(
                f"{count}/{READINGS_PER_CONDITION} -> "
                f"Temp={temperature} C, "
                f"X={accel_x}, "
                f"Y={accel_y}, "
                f"Z={accel_z}"
            )


        # ==================================================
        # CONDITION FINISHED
        # ==================================================

        print()
        print("========================================")
        print("Finished:", condition)
        print(
            "Samples collected:",
            READINGS_PER_CONDITION
        )
        print("Data added to:", CSV_FILE)
        print("========================================")
        print()


# ==================================================
# STOP PROGRAM
# ==================================================

except KeyboardInterrupt:

    print()
    print("Recording stopped by user.")


# ==================================================
# CLOSE EVERYTHING
# ==================================================

finally:

    file.close()
    ser.close()

    print()
    print("Arduino connection closed.")
    print("CSV file closed.")