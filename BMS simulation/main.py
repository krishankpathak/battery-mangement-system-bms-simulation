
from battery.pack import BatteryPack
from sim.simulator import run_simulation
from sim.plotters import plot_results
from utils.loggers import simple_logger

if __name__ == "__main__":
    pack = BatteryPack(num_cells=4, cell_capacity=2.5, cell_voltage=3.7)
    sim_time = 3600
    dt = 10

    time_data, soc_data, voltage_data = run_simulation(pack, sim_time, dt, simple_logger)
    plot_results(time_data, soc_data, voltage_data)
