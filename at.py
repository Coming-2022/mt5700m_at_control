import time
import socket
from tabulate import tabulate

# Unix Domain Socket 文件路径
SOCKET_FILE = "/tmp/at_socket.sock"

class CellularManager:
    def __init__(self):
        # Dictionary of AT commands for various operations
        self.at_commands = {
            "view_5g_nr_cc_status": "AT^HFREQINFO?",
            "view_signal": "AT^HCSQ?",
            "restart_cellular": "AT+CFUN=1,1",
            "check_lock_status": "AT^NRFREQLOCK?",
            "lock_cell_16": 'AT^NRFREQLOCK=2,0,1,"78","627264","1","16"',
            "lock_cell_334_627264": 'AT^NRFREQLOCK=2,0,1,"78","627264","1","334"',
            "lock_cell_334_633984": 'AT^NRFREQLOCK=2,0,1,"78","633984","1","334"',
            "lock_cell_579_627264": 'AT^NRFREQLOCK=2,0,1,"78","627264","1","579"',
            "lock_cell_579_633984": 'AT^NRFREQLOCK=2,0,1,"78","633984","1","579"',
            "lock_cell_default": 'AT^NRFREQLOCK=2,0,1,"78","627264","1","579"',
            "unlock_cell": "AT^NRFREQLOCK=0"
        }


    def colorize(self, text, color='black', background='yellow'):
        """
        Set the color and background color of a text string.

        Args:
            text (str): The text string to be colored.
            color (str): The color of the text. Possible values are: black, red, green, yellow, blue, magenta, cyan, white.
            background (str): The background color of the text. Possible values are: black, red, green, yellow, blue, magenta, cyan, white.

        Returns:
            str: The text string with color and background color settings.
        """
        colors = {
            'black': '30',
            'red': '31', 
            'green': '32',
            'yellow': '33',
            'blue': '34',
            'magenta': '35',
            'cyan': '36',
            'white': '37'
        }

        backgrounds = {
            'black': '40',
            'red': '41',
            'green': '42', 
            'yellow': '43',
            'blue': '44',
            'magenta': '45',
            'cyan': '46',
            'white': '47'
        }

        color_code = colors.get(color, '39') if color else '39'
        background_code = backgrounds.get(background, '49') if background else '49'

        return f"\033[{background_code}m\033[{color_code}m{text}\033[0m"

    def send_command(self, command):
        """
        Send AT command and receive response
        """
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client_socket:
                client_socket.connect(SOCKET_FILE)
                # 发送命令
                client_socket.sendall(command.encode())
                # 接收响应
                response = bytearray()
                while True:
                    data = client_socket.recv(4096)
                    if not data:
                        break
                    response.extend(data)
                    if b"No response received from server" in response:
                        break
                decoded_response = response.decode()
                if decoded_response:
                    return decoded_response
        except Exception as e:
            print(f"Error: {e}")
            return None

    def view_5g_nr_cc_status(self):
        """
        View 5G NR CC Status
        Sends AT^HFREQINFO? command to get information about 5G NR and LTE carrier components
        """
        response = self.send_command(self.at_commands.get("view_5g_nr_cc_status", ""))
        if response and "^HFREQINFO:" in response:
            response = response.split("^HFREQINFO:")[1].split("\r\nOK\r\n")[0]  # 去除响应中的 \r\n\r\nOK
            records = response.split(",")

            proa, sysmode = map(int, records[:2])  # 取出前两个字段作为 proa 和 sysmode
            records = records[2:]

            nr_records = [
                {
                    "proa": proa,
                    "sysmode": "NR",
                    "band_class": band_class,
                    "dl_fcn": dl_fcn,
                    "dl_freq": dl_freq,
                    "dl_bw": dl_bw,
                    "ul_fcn": ul_fcn,
                    "ul_freq": ul_freq,
                    "ul_bw": ul_bw,
                }
                for band_class, dl_fcn, dl_freq, dl_bw, ul_fcn, ul_freq, ul_bw in [records[i:i+7] for i in range(0, len(records), 7)]
                if sysmode == 7
            ]

            lte_records = [
                {
                    "proa": proa,
                    "sysmode": "LTE",
                    "band_class": band_class,
                    "dl_fcn": dl_fcn,
                    "dl_freq": dl_freq,
                    "dl_bw": dl_bw,
                    "ul_fcn": ul_fcn,
                    "ul_freq": ul_freq,
                    "ul_bw": ul_bw,
                }
                for band_class, dl_fcn, dl_freq, dl_bw, ul_fcn, ul_freq, ul_bw in [records[i:i+7] for i in range(0, len(records), 7)]
                if sysmode == 6
            ]

            if nr_records:
                print(self.colorize("📈 5G NR CC Status:📈",color='black',background='white'))
                for record in nr_records:
                    print(self.colorize(f"{record}",color='black',background='white'))
                print(self.colorize(f"{len(nr_records)} NR CC{'s' if len(nr_records) != 1 else ''} detected"))

            if lte_records:
                print("\n📈 LTE CC Status:📈")
                for record in lte_records:
                    print(self.colorize(f"{record}"))
                print(self.colorize(f"{len(lte_records)} NR CC{'s' if len(lte_records) != 1 else ''} detected"))

            if not nr_records and not lte_records:
                print("No NR or LTE CC records found")

        else:
            print("Invalid response format")

    def view_signal(self):
        """
        View signal strength and quality
        Sends AT^HCSQ? command to get information about signal strength and quality
        """
        response = self.send_command(self.at_commands.get("view_signal", ""))
        if response and "^HCSQ:" in response:
            response = response.split("^HCSQ:")[1].split("\r\nOK\r\n")[0]  # 去除响应中的 \r\n\r\nOK
            fields = response.strip('"').split('","')
            if len(fields) == 1:
                fields = fields[0].split(",")
            if len(fields) >= 4:
                sysmode, rsrp, sinr, rsrq = fields
                sysmode = sysmode.strip('"')  # 去除 sysmode 中的引号

                # 转换 rsrp 值
                if rsrp == "255":
                    rsrp_value = "未知或不可测"
                else:
                    rsrp_value = -140 + int(rsrp)

                # 转换 sinr 值
                if sinr == "255":
                    sinr_value = "未知或不可测"
                elif sinr == "251":
                    sinr_value = "≥ 30.0 dB"
                else:
                    sinr_value = "{:.1f} dB".format(-20 + int(sinr) * 0.2)

                # 转换 rsrq 值
                if rsrq == "255":
                    rsrq_value = "未知或不可测"
                elif rsrq == "34":
                    rsrq_value = "≥ -3 dB"
                else:
                    rsrq_value = -19.5 + int(rsrq) * 0.5

                print(self.colorize("📶Cell Signal Status: 📶",color='black',background='white'))
                print(self.colorize(f"System Mode: {sysmode}"))
                print(self.colorize(f"5g_rsrp: {rsrp_value} dBm"))
                print(self.colorize(f"5g_rsrq: {rsrq_value} dB"))
                print(self.colorize(f"5g_sinr: {sinr_value}"))
            else:
                print("Invalid response format")
        else:
            print("Invalid response format")

    def restart_cellular(self):
        """
        Restart cellular module
        Sends AT+CFUN=1,1 command to restart the cellular module
        """
        response = self.send_command(self.at_commands["restart_cellular"])
        if response:
            print(f"Cell Restart Response: {response}")

    def check_lock_status(self):
        """
        Check the current lock status
        Sends AT^NRFREQLOCK? command to check if a cell is currently locked
        """
        response = self.send_command(self.at_commands["check_lock_status"])
        if response and "^NRFREQLOCK:" in response:
            lock_status_lines = response.split("^NRFREQLOCK:")[1].split("\r\n\r\nOK")[0].split("\n")
            if len(lock_status_lines) > 3:
                locked_cell_info = lock_status_lines[2].rstrip('\r')
                print(self.colorize(f"🔒 Lock Results: {locked_cell_info}"))
            else:
                print(self.colorize(f"🔒 Lock Results: None"))
        else:
            print("Invalid response format")

    def lock_cell(self):
        """
        Lock to a specific cell
        Provides options to lock to a specific cell (579 ARFCN 627264, 334 ARFCN 627264, or 334 ARFCN 633984)
        Sends the corresponding AT^NRFREQLOCK command to lock the selected cell
        """
        print("\n Select 1CC cell to lock:")
        print("1. Cell 16 (ARFCN 627264) \n")

        print("\n Select 2CC cell to lock:")
        print("2. Cell 579 (ARFCN 627264)")
        print("3. Cell 334 (ARFCN 627264)")
        print("4. Cell 334 (ARFCN 633984)")
        print("5. Exit")
        cell_choice = input("Enter your choice (1-4): ")
        if cell_choice == "1":
            confirm = input("Are you sure you want to lock cell 16 (ARFCN 627264)? (Y/N): ")
            if confirm.upper() == "Y":
                response = self.send_command(self.at_commands["lock_cell_16"])
                if response and "OK" in response:
                    self.restart_cellular()
        if cell_choice == "2":
            confirm = input("Are you sure you want to lock cell 579 (ARFCN 627264)? (Y/N): ")
            if confirm.upper() == "Y":
                response = self.send_command(self.at_commands["lock_cell_579_627264"])
                if response and "OK" in response:
                    self.restart_cellular()
        elif cell_choice == "3":
            confirm = input("Are you sure you want to lock cell 334 (ARFCN 627264)? (Y/N): ")
            if confirm.upper() == "Y":
                response = self.send_command(self.at_commands["lock_cell_334_627264"])
                if response and "OK" in response:
                    self.restart_cellular()
        elif cell_choice == "4":
            confirm = input("Are you sure you want to lock cell 334 (ARFCN 633984)? (Y/N): ")
            if confirm.upper() == "Y":
                response = self.send_command(self.at_commands["lock_cell_334_633984"])
                if response and "OK" in response:
                    self.restart_cellular()
        elif cell_choice == "5":
            print("Exiting...")
        else:
            print("Invalid choice. Please try again.")

    def unlock_cell(self):
        """
        Unlock the currently locked cell
        Sends AT^NRFREQLOCK=0 command to unlock the currently locked cell
        """
        self.send_command(self.at_commands["unlock_cell"])
        print("Unlock Cell")

    def other_command(self):
        """
        Execute other commands like checking chip temperature or manual AT commands
        """
        while True:
            print("\n🖥️  Other Command:")
            print("1. 🌡️  Chip Temperature")
            print("2. 💻 Manually Command")
            print("3. Exit")

            choice = input("Enter your choice (1-3): ")

            if choice == "1":
                response = self.send_command("AT^CHIPTEMP?")
                if response and "^CHIPTEMP:" in response:
                    temp_values = response.split("^CHIPTEMP:")[1].split(",")
                    temp_value = int(temp_values[0])
                    formatted_temp = f"{temp_value / 10}°C"
                    print(self.colorize(f"Chip Temperature: {formatted_temp}"))
                else:
                    print("No response received or invalid response format.")
            elif choice == "2":
                command = input("Enter the command: ")
                response = self.send_command(command)
                if response:
                    print(f"Command Response: {response}")
                else:
                    print("No response received.")
            elif choice == "3":
                print("Exiting Other Command...")
                break
            else:
                print("Invalid choice. Please try again.")

# Cell Scan results handle
    def frequency_to_NR_ARFCN(self, band, freq):
        """
        Convert frequency to NR ARFCN
        Takes the band and frequency as input and returns the corresponding NR ARFCN
        """
        earfcn = ""
        if freq != "":
            if band in ["1", "5", "28", "41"]:
                earfcn = freq // 5
            elif band in ["78", "79"]:
                earfcn = (freq - 3000000) // 15 + 600000
            else:
                pass
        if not earfcn:
            earfcn = "Unknown earfcn"
        return earfcn

    def frequency_to_LTE_ARFCN(self, band, freq):
        """
        Convert frequency to LTE ARFCN
        Takes the band and frequency as input and returns the corresponding LTE ARFCN
        """
        earfcn = ""
        if freq != "":
            if band == "1":
                earfcn = freq - 21100
            elif band == "3":
                earfcn = (freq + 1200) - 18050
            elif band == "5":
                earfcn = (freq + 2400) - 8690
            elif band == "8":
                earfcn = (freq + 3450) - 9250
            elif band == "34":
                earfcn = (freq + 36200) - 20100
            elif band == "38":
                earfcn = (freq + 37750) - 25700
            elif band == "39":
                earfcn = (freq + 38250) - 18800
            elif band == "40":
                earfcn = (freq + 38650) - 23000
            elif band == "41":
                earfcn = (freq + 39650) - 24960
            else:
                pass
        if not earfcn:
            earfcn = "Unknown earfcn"
        return earfcn
    
    def parse_cellscan_response(self, response_results):
        """
        Parse the response from the AT^CELLSCAN=3 command
        Returns a list of records containing information about the scanned cells
        """
        result = []
        lines = response_results.split("\n")
        for line in lines:
            if line.startswith("^CELLSCAN: "):
                line = line.split(": ", 1)[1]  # 去掉开头的 "^CELLSCAN: "
                fields = line.split(",")
                rat = int(fields[0])
                if rat == 1:
                    rat_str = "UMTS (FDD)"
                elif rat == 2:
                    rat_str = "LTE"
                elif rat == 3:
                    rat_str = "NR"
                else:
                    rat_str = "Unknown"
                plmn = fields[1].strip('"')
                freq = int(fields[2])
                pci = int(fields[3]) if fields[3] else None
                band = int(fields[4], 16)
                lac = int(fields[5], 16)
                scs = int(fields[10]) if fields[10] else None
                scs_value = None
                if scs == 0:
                    scs_value = "15"
                elif scs == 1:
                    scs_value = "30"
                elif scs == 2:
                    scs_value = "60"
                elif scs == 3:
                    scs_value = "120"
                elif scs == 4:
                    scs_value = "240"
                rsrp = int(fields[11]) if fields[11] else None
                rsrq = int(fields[12]) * 0.5 if fields[12] else None
                sinr = int(fields[13]) * 0.5 if fields[13] else None
                lte_sinr = int(fields[14], 16) * 0.125 if fields[14] else None

                if rat_str == "NR":
                    arfcn = self.frequency_to_NR_ARFCN(str(band), freq)
                elif rat_str == "LTE":
                    arfcn = self.frequency_to_LTE_ARFCN(str(band), freq)
                else:
                    arfcn = "Unknown arfcn"

                record = [rat_str, plmn, freq, pci, band, lac, scs_value, rsrp, rsrq, sinr, lte_sinr, arfcn]
                result.append(record)

        return result

    def initial_configuration(self):
        """
        Perform initial configuration for cell scanning
        Sends a series of AT commands to configure the device for cell scanning
        """
        print("Performing Initial Configuration...")
        commands = [
            "AT^C5GOPTION=1,1,1",
            "AT^LTEFREQLOCK=0",
            "AT^NRFREQLOCK=0",
            "AT^SYSCFGEX=\"0803\",3FFFFFFF,1,2,7FFFFFFFFFFFFFFF,,"
        ]
        for command in commands:
            response = self.send_command(command)
            while "OK" not in response:
                print(f"Command '{command}' failed. Retrying...")
                time.sleep(2)
                response = self.send_command(command)
            print(f"Command '{command}' executed successfully.")
            time.sleep(1)

    def scan_cell(self):
        """
        Perform cell scan
        Unlocks the cell, sends AT+COPS=2 and AT^CELLSCAN=3 commands to scan for cells
        Parses the response
        """
        print(self.colorize(f"Action: Performing Cell Scan..."))
        print(self.colorize(f"Will restart 5G chip, need 1~2 mins return results."))

        # Unlock cell
        self.unlock_cell()

        # 执行 AT+COPS=2
        response = self.send_command("AT+COPS=2")
        while "OK" not in response:
            print("Command 'AT+COPS=2' failed. Retrying...")
            time.sleep(2)
            response = self.send_command("AT+COPS=2")
        print("Command 'AT+COPS=2' executed successfully.")

        # 执行 AT^CELLSCAN=3
        response = ""
        cellscan_completed = False
        while not cellscan_completed:
            print("Waiting for 'AT^CELLSCAN=3' to complete...")
            time.sleep(2)
            new_response = self.send_command("AT^CELLSCAN=3")
            if new_response is not None:
                response += new_response
                if "OK" in new_response:
                    cellscan_completed = True
            else:
                print("No response received. Retrying...")

        # Scan Reults Data Format Handle
        try:
            cellscan_data = self.parse_cellscan_response(response)
            if cellscan_data:
                headers = ["rat", "plmn", "KHz(freq)", "pci", "band", "lac", "NR_SCS_KHz", "NR_RSRP_dBm", "NR_RSRQ_dB", "NR_SINR_dB", "LTE_SINR_dB", "arfcn"]
                sorted_data = sorted(cellscan_data, key=lambda x: (-int(x[6]) if x[6] else float('-inf'), -x[7] if x[7] is not None else float('-inf'), -x[9] if x[9] is not None else float('-inf'), -x[8] if x[8] is not None else float('-inf')))
                print(tabulate(sorted_data, headers=headers, tablefmt="grid"))
            else:
                print("No valid data received from 'AT^CELLSCAN=3'")
        except Exception as e:
            print(f"Exception for Data processing: {e}")
        finally:
            # 执行 AT+COPS=0
            response = self.send_command("AT+COPS=0")
            while "OK" not in response:
                print("Command 'AT+COPS=0' failed. Retrying...")
                time.sleep(2)
                response = self.send_command("AT+COPS=0")
            print("Command 'AT+COPS=0' executed successfully.")

            # lock default cell
            print(self.colorize(f"🔒 Lock Default Cell, it will restart 5G chip."))
            print(self.colorize(f"🖥️  Will need 1~2 mins return to normal."))
            response = self.send_command(self.at_commands["lock_cell_default"])
            if response and "OK" in response:
                self.restart_cellular()

def main():
    manager = CellularManager()

    while True:
        print("\n 🌍 Simple Tool to Control MT5700M-CN AT PHY 🌍")
        print("Please select an option:\n")
        print("1. 📈 5G NR CC Status")
        print("2. 📶 View Signal")
        print("3. 🔒 Lock Status")
        print("4. 🔍 Scan Cell")
        print("5. 🔋 Restart Cellular")
        print("6. 🖥️  Other Command")
        print("7. ⏹ Exit")

        choice = input("Enter your choice (1-7): ")

        if choice == "1":
            manager.view_5g_nr_cc_status()
        elif choice == "2":
            manager.view_signal()
        elif choice == "3":
            manager.check_lock_status()
            print("\n Lock Status Options:")
            print("1. 🔒 Lock Cell")
            print("2. 🔓 Unlock Cell")
            print("3. 🔙 Back")
            lock_choice = input("Enter your choice (1-3): ")
            if lock_choice == "1":
                manager.lock_cell()
            elif lock_choice == "2":
                manager.unlock_cell()
            elif lock_choice == "3":
                pass
            else:
                print("Invalid choice. Please try again.")
        elif choice == "4":
            print("\nScan Cell Options:")
            print("1. ⚙️ Initial Configuration")
            print("2. 🔍 Scan Cell")
            print("3. 🔙 Back")
            scan_choice = input("Enter your choice (1-3): ")
            if scan_choice == "1":
                manager.initial_configuration()
            elif scan_choice == "2":
                manager.scan_cell()
            elif scan_choice == "3":
                pass
            else:
                print("Invalid choice. Please try again.")
        elif choice == "5":
            confirm = input("Are you sure you want to restart cellular? (Y/N): ")
            if confirm.upper() == "Y":
                manager.restart_cellular()
        elif choice == "6":
            manager.other_command()
        elif choice == "7":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()