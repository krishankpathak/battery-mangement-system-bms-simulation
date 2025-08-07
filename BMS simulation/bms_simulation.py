
import numpy as np
import matplotlib.pyplot as plt

# ============================
# 🔋 Battery Cell Definition
# ============================

class BatteryCell:
    def __init__(self, capacity_ah, voltage_nominal, initial_soc=100, initial_soh=100, initial_temp=25):
        self.capacity_ah = capacity_ah                # Battery capacity in Ah
        self.voltage_nominal = voltage_nominal        # Nominal voltage in Volts
        self.soc = initial_soc                        # State of Charge (%)
        self.soh = initial_soh                        # State of Health (%)
        self.temp = initial_temp                      # Cell temperature (°C)
        self.voltage = voltage_nominal                # Starting voltage

        # Thermal properties
        self.thermal_resistance = 0.1                 # °C/W (not actively used here)
        self.thermal_capacity = 500                   # J/°C (thermal mass)
        self.ambient_temp = 25                        # Ambient (room) temperature

    # ⚡ Update the voltage based on SOC and SOH
    def update_voltage(self):
        capacity_effect = self.soh / 100
        self.voltage = self.voltage_nominal * (self.soc / 100) * capacity_effect

    # 🔻 Discharge logic
    def discharge(self, current, dt):
        delta_ah = current * dt / 3600
        soc_drop = (delta_ah / self.capacity_ah) * 100
        self.soc = max(self.soc - soc_drop, 0)
        self.generate_heat(current, dt)
        self.update_voltage()

    # 🔼 Charge logic
    def charge(self, current, dt):
        delta_ah = current * dt / 3600
        soc_gain = (delta_ah / self.capacity_ah) * 100
        self.soc = min(self.soc + soc_gain, 100)
        self.generate_heat(current, dt)
        self.update_voltage()

    # 🧓 Health degradation based on cycles
    def degrade_health(self, cycles):
        self.soh -= 0.01 * cycles  # 0.01% degradation per cycle
        if self.soh < 60:
            self.soh = 60  # Minimum SOH threshold

    # 🌡️ Heat generation due to internal resistance
    def generate_heat(self, current, dt):
        resistance = 0.05  # Ohmic resistance in ohms
        heat_generated = (current ** 2) * resistance * dt  # Joules = I²R * time
        delta_temp = heat_generated / self.thermal_capacity
        self.temp += delta_temp
        self.cool_down()

    # ❄️ Cooling effect based on ambient temperature
    def cool_down(self):
        cooling_rate = (self.temp - self.ambient_temp) * 0.01
        self.temp -= cooling_rate


# ============================
# 🔋 Battery Pack Definition
# ============================

class BatteryPack:
    def __init__(self, num_cells, cell_capacity, cell_voltage):
        self.cells = [BatteryCell(cell_capacity, cell_voltage) for _ in range(num_cells)]
        self.cycles = 0

    def simulate_step(self, current, dt):
        for cell in self.cells:
            if current > 0:
                cell.discharge(current, dt)
            elif current < 0:
                cell.charge(-current, dt)

        # 📉 Track full cycles to degrade SOH
        if all(cell.soc == 100 for cell in self.cells) or all(cell.soc == 0 for cell in self.cells):
            self.cycles += 1
            for cell in self.cells:
                cell.degrade_health(self.cycles)

    # 📏 Return average and total values
    def get_pack_voltage(self):
        return sum(cell.voltage for cell in self.cells)

    def get_average_soc(self):
        return sum(cell.soc for cell in self.cells) / len(self.cells)

    def get_average_temp(self):
        return sum(cell.temp for cell in self.cells) / len(self.cells)

    def get_average_soh(self):
        return sum(cell.soh for cell in self.cells) / len(self.cells)


# ============================
# 🚀 Simulation Configuration
# ============================

sim_time = 7200  # total time: 2 hours = 7200 seconds
dt = 10          # time step: 10 seconds
num_steps = sim_time // dt

pack = BatteryPack(num_cells=4, cell_capacity=2.5, cell_voltage=3.7)

# For plotting
time_data = []
soc_data = []
temp_data = []
voltage_data = []
soh_data = []

# ============================
# ⏱️ Simulation Loop
# ============================

for step in range(num_steps):
    time = step * dt
    current = 1.0 if time < 3600 else -1.0  # 1 hour discharge, 1 hour charge
    pack.simulate_step(current, dt)

    # Store data
    time_data.append(time / 60)  # Convert to minutes
    soc_data.append(pack.get_average_soc())
    temp_data.append(pack.get_average_temp())
    voltage_data.append(pack.get_pack_voltage())
    soh_data.append(pack.get_average_soh())

# ============================
# 📊 Plotting Results
# ============================

# SOC Plot
plt.figure()
plt.plot(time_data, soc_data, label='Average SOC (%)')
plt.xlabel('Time (min)')
plt.ylabel('State of Charge (%)')
plt.title('Battery SOC Over Time')
plt.grid(True)
plt.legend()
plt.show()

# Temperature Plot
plt.figure()
plt.plot(time_data, temp_data, label='Avg Temperature (°C)', color='red')
plt.xlabel('Time (min)')
plt.ylabel('Temperature (°C)')
plt.title('Battery Temperature Over Time')
plt.grid(True)
plt.legend()
plt.show()

# SOH Plot
plt.figure()
plt.plot(time_data, soh_data, label='Average SOH (%)', color='green')
plt.xlabel('Time (min)')
plt.ylabel('State of Health (%)')
plt.title('Battery SOH Over Time')
plt.grid(True)
plt.legend()
plt.show()
