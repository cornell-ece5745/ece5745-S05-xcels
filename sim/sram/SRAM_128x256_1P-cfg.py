word_size = 128
num_words = 256
num_banks = 1

num_rw_ports = 1
num_r_ports = 0
num_w_ports = 0

tech_name = "freepdk45"

nominal_corners_only = True
process_corners = ["TT"]
supply_voltages = [1.1]
temperatures = [25]

route_supplies = True
check_lvsdrc = True

output_path = "SRAM_128x256_1P_inner"
output_name = "SRAM_128x256_1P_inner"

instance_name = "SRAM_128x256_1P"
