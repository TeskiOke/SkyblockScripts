import asyncio
import sys
import winrt.windows.devices.bluetooth as bt
import winrt.windows.networking.sockets as sockets
import winrt.windows.storage.streams as streams

# CRC16-Xmodem lookup table from MelianMiko
crc16_tab = [0, 4129, 8258, 12387, 16516, 20645, 24774, 28903, -32504, -28375, -24246, -20117, -15988, -11859,
             -7730,
             -3601, 4657, 528, 12915, 8786, 21173, 17044, 29431, 25302, -27847, -31976, -19589, -23718, -11331,
             -15460, -3073, -7202, 9314, 13379, 1056, 5121, 25830, 29895, 17572, 21637, -23190, -19125, -31448,
             -27383, -6674, -2609, -14932, -10867, 13907, 9842, 5649, 1584, 30423, 26358, 22165, 18100, -18597,
             -22662, -26855, -30920, -2081, -6146, -10339, -14404, 18628, 22757, 26758, 30887, 2112, 6241, 10242,
             14371, -13876, -9747, -5746, -1617, -30392, -26263, -22262, -18133, 23285, 19156, 31415, 27286, 6769,
             2640, 14899, 10770, -9219, -13348, -1089, -5218, -25735, -29864, -17605, -21734, 27814, 31879, 19684,
             23749, 11298, 15363, 3168, 7233, -4690, -625, -12820, -8755, -21206, -17141, -29336, -25271, 32407,
             28342, 24277, 20212, 15891, 11826, 7761, 3696, -97, -4162, -8227, -12292, -16613, -20678, -24743,
             -28808, -28280, -32343, -20022, -24085, -12020, -16083, -3762, -7825, 4224, 161, 12482, 8419, 20484,
             16421, 28742, 24679, -31815, -27752, -23557, -19494, -15555, -11492, -7297, -3234, 689, 4752, 8947,
             13010, 16949, 21012, 25207, 29270, -18966, -23093, -27224, -31351, -2706, -6833, -10964, -15091, 13538,
             9411, 5280, 1153, 29798, 25671, 21540, 17413, -22565, -18438, -30823, -26696, -6305, -2178, -14563,
             -10436, 9939, 14066, 1681, 5808, 26199, 30326, 17941, 22068, -9908, -13971, -1778, -5841, -26168,
             -30231, -18038, -22101, 22596, 18533, 30726, 26663, 6336, 2273, 14466, 10403, -13443, -9380, -5313,
             -1250, -29703, -25640, -21573, -17510, 19061, 23124, 27191, 31254, 2801, 6864, 10931, 14994, -722,
             -4849, -8852, -12979, -16982, -21109, -25112, -29239, 31782, 27655, 23652, 19525, 15522, 11395, 7392,
             3265, -4321, -194, -12451, -8324, -20581, -16454, -28711, -24584, 28183, 32310, 20053, 24180, 11923,
             16050, 3793, 7920]

def crc16(data):
    s = 0
    for byte in data:
        s = crc16_tab[((s >> 8) ^ byte) & 255] ^ (s << 8)
        s = s & 0b1111111111111111
    return s.to_bytes(2, "big")

def build_packet(cmd: bytes, parameters=None):
    if parameters is None:
        parameters = []
    body = cmd
    for p_type, p_value in parameters:
        p_type_byte = p_type.to_bytes(1, byteorder="big")
        p_length_byte = len(p_value).to_bytes(1, byteorder="big")
        body += p_type_byte + p_length_byte + p_value
        
    result = b"Z" + (len(body) + 1).to_bytes(2, byteorder="big") + b"\x00" + body
    result += crc16(result)
    return result

def parse_packets(data: bytes):
    packets = []
    i = 0
    while i < len(data):
        if data[i] != 90: # 'Z'
            i += 1
            continue
        if i + 3 >= len(data):
            break
        length = int.from_bytes(data[i+1:i+3], byteorder="big")
        if i + length + 5 > len(data):
            break
        
        packet_data = data[i:i + length + 5]
        command_id = packet_data[4:6]
        position = 6
        parameters = []
        while position < length + 3:
            if position + 1 >= len(packet_data):
                break
            p_type = packet_data[position]
            p_length = packet_data[position + 1]
            if position + 2 + p_length > len(packet_data):
                break
            p_value = packet_data[position + 2:position + p_length + 2]
            parameters.append((p_type, p_value))
            position += p_length + 2
        
        packets.append((command_id, parameters))
        i += length + 5
    return packets

async def read_loop(reader, socket):
    try:
        while True:
            await reader.load_async(1024)
            if reader.unconsumed_buffer_length > 0:
                buf = bytearray(reader.unconsumed_buffer_length)
                reader.read_bytes(buf)
                data = bytes(buf)
                
                # Parse packet
                packets = parse_packets(data)
                for cmd_id, params in packets:
                    cmd_hex = cmd_id.hex()
                    if cmd_hex == "0127": # Battery state changed notification
                        left_bat, right_bat, case_bat = "Unknown", "Unknown", "Unknown"
                        left_chg, right_chg, case_chg = "Unknown", "Unknown", "Unknown"
                        
                        # Find Param Type 2 (battery levels) and Param Type 3 (charging states)
                        for p_type, p_val in params:
                            if p_type == 2 and len(p_val) >= 3:
                                left_bat, right_bat, case_bat = p_val[0], p_val[1], p_val[2]
                            elif p_type == 3 and len(p_val) >= 3:
                                # 100 means charging, or check specific bytes
                                # 0 means not charging
                                left_chg = "Yes" if p_val[0] > 0 else "No"
                                right_chg = "Yes" if p_val[1] > 0 else "No"
                                case_chg = "Yes" if p_val[2] > 0 else "No"
                        
                        print(f"\n[BATTERY UPDATE]")
                        print(f"  Left Earbud:  {left_bat}% (Charging: {left_chg})")
                        print(f"  Right Earbud: {right_bat}% (Charging: {right_chg})")
                        print(f"  Charging Case: {case_bat}% (Charging: {case_chg})")
                    elif cmd_hex == "2b2a": # Current ANC mode response
                        mode_name = "Unknown"
                        for p_type, p_val in params:
                            if p_type == 1 and len(p_val) > 0:
                                mode_val = p_val[0]
                                if mode_val == 0:
                                    mode_name = "Off (Normal)"
                                elif mode_val == 1:
                                    mode_name = "Active Noise Cancellation (ANC ON)"
                                elif mode_val == 2:
                                    mode_name = "Awareness (Ambient)"
                                else:
                                    mode_name = f"Custom Mode {mode_val}"
                        print(f"\n[ANC MODE STATUS] Current Mode: {mode_name}")
                    else:
                        print(f"\n[PACKET RECEIVED] Command ID: {cmd_hex}")
                        for p_type, p_val in params:
                            print(f"  Param {p_type}: hex={p_val.hex()}, raw={list(p_val)}")
                
                print("\n> ", end="", flush=True)
            await asyncio.sleep(0.1)
    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"\nReader loop error: {e}")

async def main():
    mac_str = "14:16:99:F0:6E:89"
    mac_int = int(mac_str.replace(":", ""), 16)
    
    print(f"Connecting to device with address {mac_str}...")
    try:
        device = await bt.BluetoothDevice.from_bluetooth_address_async(mac_int)
    except Exception as e:
        print(f"Error finding device: {e}")
        return
        
    if not device:
        print("Device not found. Make sure it is paired and turned on.")
        return
        
    print(f"Device found: {device.name}. Querying RFCOMM services...")
    services_result = await device.get_rfcomm_services_async()
    spp_service = None
    for svc in services_result.services:
        if "1101" in svc.service_id.as_string():
            spp_service = svc
            break
            
    if not spp_service:
        print("SPP Serial Port service not found on this device.")
        return
        
    print("Opening StreamSocket...")
    socket = sockets.StreamSocket()
    try:
        await socket.connect_async(spp_service.connection_host_name, spp_service.connection_service_name)
    except Exception as e:
        print(f"Failed to connect socket: {e}")
        return
        
    print("Connected successfully!")
    
    writer = streams.DataWriter(socket.output_stream)
    reader = streams.DataReader(socket.input_stream)
    reader.input_stream_options = streams.InputStreamOptions.PARTIAL
    
    # Start reader task
    read_task = asyncio.create_task(read_loop(reader, socket))
    
    print("\n=== Earbuds Interactive Control CLI ===")
    print("Commands:")
    print("  battery    - Request battery info")
    print("  anc_query  - Query current Active Noise Cancellation status")
    print("  anc_on     - Turn on Noise Cancellation")
    print("  anc_off    - Turn off Noise Cancellation")
    print("  awareness  - Turn on Ambient/Awareness mode")
    print("  exit       - Disconnect and exit")
    print("=======================================")
    
    loop = asyncio.get_running_loop()
    
    while True:
        try:
            # Read command from stdin without blocking event loop
            user_input = await loop.run_in_executor(None, sys.stdin.readline)
            user_input = user_input.strip().lower()
            
            if not user_input:
                continue
                
            if user_input == "exit":
                break
            elif user_input == "battery":
                pkt = build_packet(b"\x01\x08")
                writer.write_bytes(pkt)
                await writer.store_async()
            elif user_input == "anc_query":
                pkt = build_packet(b"\x2b\x2a")
                writer.write_bytes(pkt)
                await writer.store_async()
            elif user_input == "anc_off":
                pkt = build_packet(b"\x2b\x04", [(1, b"\x00")])
                print("Sending ANC Off command...")
                writer.write_bytes(pkt)
                await writer.store_async()
            elif user_input == "anc_on":
                pkt = build_packet(b"\x2b\x04", [(1, b"\x01")])
                print("Sending ANC On command...")
                writer.write_bytes(pkt)
                await writer.store_async()
            elif user_input == "awareness":
                pkt = build_packet(b"\x2b\x04", [(1, b"\x02")])
                print("Sending Awareness command...")
                writer.write_bytes(pkt)
                await writer.store_async()
            else:
                print(f"Unknown command: '{user_input}'")
        except Exception as e:
            print(f"Error handling command: {e}")
            
    print("Disconnecting...")
    read_task.cancel()
    try:
        await read_task
    except asyncio.CancelledError:
        pass
    socket.close()
    print("Disconnected. Goodbye!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
