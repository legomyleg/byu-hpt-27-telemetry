from pathlib import Path

from rocketpy import Environment, Rocket, SolidMotor, Flight
import numpy as np
import matplotlib.pyplot as plt
from numpy.random import normal, choice
from IPython.display import display
from time import process_time, time
from imageio import imread
from matplotlib.patches import Ellipse

REPO_ROOT = Path(__file__).resolve().parents[2]
RESOURCE_DIR = REPO_ROOT / "resources" / "rocketpy"
OUTPUT_DIR = REPO_ROOT / "resources" / "sim_data" / "monte_carlo"

def runMonteCarlo(numberOfSimulations, month, day, year, hour):
    analysis_parameters = {
        # Mass Details
        # Rocket's dry mass without motor (kg) and its uncertainty (standard deviation)
        "rocket_mass": [17.52],
        # Rocket's inertia moment perpendicular to its axis (kg*m^2)
        "rocket_inertia_11": [7.5811],
        # Rocket's inertia moment relative to its axis (kg*m^2)
        "rocket_inertia_33": [0.109],
        # Motors's dry mass without propellant (kg) and its uncertainty (standard deviation)
        "motor_dry_mass": [7.004],
        # Motor's dry inertia moment perpendicular to its axis (kg*m^2)
        "motor_inertia_11": [1.329],
        # Motors's dry inertia moment relative to its axis (kg*m^2)
        "motor_inertia_33": [0.002],
        # Distance between nozzle and the center of motor dry mass (positive)
        "motor_dry_mass_position": [.753],
        # Propulsion Details - run help(SolidMotor) for more information
        # Motor total impulse (N*s)
        "impulse": (21384.0, 1069.2),
        # Motor burn out time (s)
        "burn_time": (3.997, .05),
        # Motor's nozzle radius (m)
        "nozzle_radius": [49 / 1000],
        # Motor's nozzle throat radius (m)
        "throat_radius": [49 / 1000],
        # Motor's grain separation (axial distance between two grains) (m)
        "grain_separation": [1 / 1000],
        # Motor's grain density (kg/m^3)
        "grain_density": (949.2, 9),
        # Motor's grain outer radius (m)
        "grain_outer_radius": [49 / 1000],
        # Motor's grain inner radius (m)
        "grain_initial_inner_radius": [15 / 1000],
        # Motor's grain height (m)
        "grain_initial_height": [1507 / 1000],
        # Aerodynamic Details - run help(Rocket) for more information
        # Rocket's radius (kg*m^2)
        "radius": [78 / 1000],
        # Distance between nozzle and nozzle (m)
        "nozzle_position": [0],
        # Distance between nozzle and center of grains mass (positive)
        "grains_center_of_mass_position": [.753],
        # Multiplier for rocket's drag curve. Usually has a mean value of 1 and a uncertainty of 5% to 10%
        "power_off_drag": (0.9081 / 1.05, 0.033),
        # Multiplier for rocket's drag curve. Usually has a mean value of 1 and a uncertainty of 5% to 10%
        "power_on_drag": (0.9081 / 1.05, 0.033),
        # Rocket's nose cone length (m)
        "nose_length": [0.673],
        # Axial distance between rocket's center of dry mass and nearest point in its nose cone (m)
        "nose_distance_to_CM": [.576],
        # Fin span (m)
        "fin_span": [0.1275],
        # Fin root chord (m)
        "fin_root_chord": [0.203],
        # Fin tip chord (m)
        "fin_tip_chord": [0.061],
        # Axial distance between rocket's center of dry mass and nearest point in its fin (m)
        "fin_distance_to_CM": [-1.505],
        # Launch and Environment Details - run help(Environment) and help(Flight) for more information
        # Launch rail inclination angle relative to the horizontal plane (degrees)
        "inclination": [84],
        # Launch rail heading relative to north (degrees)
        "heading": (193, 2),
        # Launch rail length (m)
        "rail_length": [5.2],
        # Members of the ensemble forecast to be used
        "ensemble_member": list(range(30)),
        # Parachute Details - run help(Rocket) for more information
        # Drag coefficient times reference area for the drogue chute (m^2)
        "cd_s_drogue": (0.5253543144, 0.17),
        # Drag coefficient times reference area for the main chute (m^2)
        "cd_s_main": (10.273, 1.0),
        # Time delay between parachute ejection signal is detected and parachute is inflated (s)
        "lag_rec": (1, 0.5),
        # Electronic Systems Details - run help(Rocket) for more information
        # Time delay between sensor signal is received and ejection signal is fired (s)
        "lag_se": (0.73, 0.16),
    }

    def flight_settings(analysis_parameters, total_number):
        i = 0
        while i < total_number:
            # Generate a flight setting
            flight_setting = {}
            for parameter_key, parameter_value in analysis_parameters.items():
                if type(parameter_value) is tuple:
                    # Ensure both mean and standard deviation are floats
                    mean, std_dev = parameter_value
                    flight_setting[parameter_key] = normal(float(mean), float(std_dev))
                else:
                    flight_setting[parameter_key] = choice(parameter_value)

            # Skip if certain values are negative, which happens due to the normal curve but isn't realistic
            if flight_setting["lag_rec"] < 0 or flight_setting["lag_se"] < 0:
                continue

            # Update counter
            i += 1
            # Yield a flight setting
            yield flight_setting
            
    def export_flight_data(flight_setting, flight_data, exec_time):
        # Generate flight results
        flight_result = {
            "out_of_rail_time": flight_data.out_of_rail_time,
            "out_of_rail_velocity": flight_data.out_of_rail_velocity,
            "max_velocity": flight_data.speed.max,
            "apogee_time": flight_data.apogee_time,
            "apogee_altitude": flight_data.apogee - Env.elevation,
            "apogee_x": flight_data.apogee_x,
            "apogee_y": flight_data.apogee_y,
            "impact_time": flight_data.t_final,
            "impact_x": flight_data.x_impact,
            "impact_y": flight_data.y_impact,
            "impact_velocity": flight_data.impact_velocity,
            "initial_static_margin": flight_data.rocket.static_margin(0),
            "out_of_rail_static_margin": flight_data.rocket.static_margin(
                flight_data.out_of_rail_time
            ),
            "final_static_margin": flight_data.rocket.static_margin(
                flight_data.rocket.motor.burn_out_time
            ),
            "number_of_events": len(flight_data.parachute_events),
            "execution_time": exec_time,
        }

        # Take care of parachute results
        if len(flight_data.parachute_events) > 0:
            flight_result["drogue_triggerTime"] = flight_data.parachute_events[0][0]
            flight_result["drogue_inflated_time"] = (
                flight_data.parachute_events[0][0] + flight_data.parachute_events[0][1].lag
            )
            flight_result["drogue_inflated_velocity"] = flight_data.speed(
                flight_data.parachute_events[0][0] + flight_data.parachute_events[0][1].lag
            )
            flight_result["main_triggerTime"] = flight_data.parachute_events[1][0]
            flight_result["main_inflated_time"] = (
                flight_data.parachute_events[1][0] + flight_data.parachute_events[1][1].lag
            )
            flight_result["main_inflated_velocity"] = flight_data.speed(
                flight_data.parachute_events[1][0] + flight_data.parachute_events[1][1].lag
            )
        else:
            flight_result["drogue_triggerTime"] = 0
            flight_result["drogue_inflated_time"] = 0
            flight_result["drogue_inflated_velocity"] = 0
            flight_result["main_triggerTime"] = 0
            flight_result["main_inflated_time"] = 0
            flight_result["main_inflated_velocity"] = 0\

        # Write flight setting and results to file
        dispersion_input_file.write(str(flight_setting) + "\n")
        dispersion_output_file.write(str(flight_result) + "\n")


    def export_flight_error(flight_setting):
        dispersion_error_file.write(str(flight_setting) + "\n")
        
    # Basic analysis info
    filename = "MonteCarlo"
    number_of_simulations = numberOfSimulations

    # Create data files for inputs, outputs and error logging
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    dispersion_error_file = (OUTPUT_DIR / f"{filename}.disp_errors.txt").open("w")
    dispersion_input_file = (OUTPUT_DIR / f"{filename}.disp_inputs.txt").open("w")
    dispersion_output_file = (OUTPUT_DIR / f"{filename}.disp_outputs.txt").open("w")

    # Initialize counter and timer
    i = 0

    initial_wall_time = time()
    initial_cpu_time = process_time()

    Env = Environment(date=(year, month, day, hour), latitude=32.94103529050622, longitude=-106.92203686488024, elevation=1385)
    Env.set_atmospheric_model(
        type="Ensemble",
        file="GEFS"
    )

    # Iterate over flight settings
    out = display("Starting", display_id=True)
    for setting in flight_settings(analysis_parameters, number_of_simulations):
        start_time = process_time()
        i += 1

        # Update environment object
        Env.select_ensemble_member(setting["ensemble_member"])

        # Create motor
        monteCarloMotor = SolidMotor(
            thrust_source=str(RESOURCE_DIR / "AeroTech_O5500X-PS.eng"),
            burn_time=3.997,
            reshape_thrust_curve=(setting["burn_time"], setting["impulse"]),
            nozzle_radius=setting["nozzle_radius"],
            throat_radius=setting["throat_radius"],
            grain_number=1,
            grain_separation=setting["grain_separation"],
            grain_density=setting["grain_density"],
            grain_outer_radius=setting["grain_outer_radius"],
            grain_initial_inner_radius=setting["grain_initial_inner_radius"],
            grain_initial_height=setting["grain_initial_height"],
            interpolation_method="linear",
            coordinate_system_orientation="nozzle_to_combustion_chamber",
            nozzle_position=setting["nozzle_position"],
            grains_center_of_mass_position=setting["grains_center_of_mass_position"],
            dry_mass=setting["motor_dry_mass"],
            dry_inertia=(
                setting["motor_inertia_11"],
                setting["motor_inertia_11"],
                setting["motor_inertia_33"],
            ),
            center_of_dry_mass_position=setting["motor_dry_mass_position"],
        )
        # Create rocket
        MonteCarloRocket2 = Rocket(
            radius=setting["radius"],
            mass=setting["rocket_mass"],
            inertia=(
                setting["rocket_inertia_11"],
                setting["rocket_inertia_11"],
                setting["rocket_inertia_33"],
            ),
            power_off_drag=str(RESOURCE_DIR / "Escalante 30k v1.5cdpoweroff.CSV"),
            power_on_drag=str(RESOURCE_DIR / "Escalante 30k v1.5cdpoweron.CSV"),
            center_of_mass_without_motor=0,
            coordinate_system_orientation="tail_to_nose",
        )
        MonteCarloRocket2.set_rail_buttons(-1.3413486, -1.6207486, 45)

        MonteCarloRocket2.add_motor(monteCarloMotor, position=-1.872)

        # Edit rocket drag
        MonteCarloRocket2.power_off_drag *= setting["power_off_drag"]
        MonteCarloRocket2.power_on_drag *= setting["power_on_drag"]
        
        # Add rocket nose, fins and tail
        NoseCone = MonteCarloRocket2.add_nose(
            length=setting["nose_length"],
            kind="ogive",
            position=setting["nose_distance_to_CM"] + setting["nose_length"],
        )
        FinSet = MonteCarloRocket2.add_trapezoidal_fins(
            n=4,
            span=setting["fin_span"],
            root_chord=setting["fin_root_chord"],
            tip_chord=setting["fin_tip_chord"],
            position=setting["fin_distance_to_CM"],
            sweep_length=0.203,
            cant_angle=0,
            airfoil=(str(RESOURCE_DIR / "NACA0012-radians.csv"), "radians"),
        )
        # Add parachute
        Drogue = MonteCarloRocket2.add_parachute(
            "Drogue",
            cd_s=setting["cd_s_drogue"],
            trigger="apogee",
            sampling_rate=105,
            lag=setting["lag_rec"] + setting["lag_se"],
            noise=(0, 8.3, 0.5),
        )
        
        Main = MonteCarloRocket2.add_parachute(
            "Main",
            cd_s=setting["cd_s_main"],
            trigger=1500,
            sampling_rate=105,
            lag=setting["lag_rec"] + setting["lag_se"],
            noise=(0, 8.3, 0.5),
        )
        
        tail_1 = MonteCarloRocket2.add_tail(
            top_radius=0.078, bottom_radius=0.0711, length=0.051, position=-1.708
        )
        tail_2 = MonteCarloRocket2.add_tail(
            top_radius=0.0711, bottom_radius=0.064, length=0.1, position=-1.759
        )
        tail_3 = MonteCarloRocket2.add_tail(
            top_radius=0.064, bottom_radius=0.0535, length=0.013, position=-1.859
        )
        
        # Run trajectory simulation
        try:
            test_flight = Flight(
                rocket=MonteCarloRocket2,
                environment=Env,
                rail_length=setting["rail_length"],
                inclination=setting["inclination"],
                heading=setting["heading"],
                max_time=1200,
            )
            export_flight_data(setting, test_flight, process_time() - start_time)
        except Exception as E:
            print(E)
            export_flight_error(setting)

        # Register time
        out.update(
            f"Curent iteration: {i:06d} | Average Time per Iteration: {(process_time() - initial_cpu_time)/i:2.6f} s"
        )

    # Done

    ## Print and save total time
    final_string = f"Completed {i} iterations successfully. Total CPU time: {process_time() - initial_cpu_time} s. Total wall time: {time() - initial_wall_time} s"
    out.update(final_string)
    dispersion_input_file.write(final_string + "\n")
    dispersion_output_file.write(final_string + "\n")
    dispersion_error_file.write(final_string + "\n")

    ## Close files
    dispersion_input_file.close()
    dispersion_output_file.close()
    dispersion_error_file.close()
    return "Completed"

def importMonteCarloResults():
    filename = "MonteCarlo"

    # Initialize variable to store all results
    dispersion_general_results = []

    dispersion_results = {
        "out_of_rail_time": [],
        "out_of_rail_velocity": [],
        "apogee_time": [],
        "apogee_altitude": [],
        "apogee_x": [],
        "apogee_y": [],
        "impact_time": [],
        "impact_x": [],
        "impact_y": [],
        "impact_velocity": [],
        "initial_static_margin": [],
        "out_of_rail_static_margin": [],
        "final_static_margin": [],
        "number_of_events": [],
        "max_velocity": [],
        "drogue_triggerTime": [],
        "drogue_inflated_time": [],
        "drogue_inflated_velocity": [],
        "execution_time": [],
        "main_triggerTime": [],
        "main_inflated_time": [],
        "main_inflated_velocity": [],    
    }

    # Get all dispersion results
    dispersion_output_file = (OUTPUT_DIR / f"{filename}.disp_outputs.txt").open("r")

    # Read each line of the file and convert to dict
    for line in dispersion_output_file:
        # Skip comments lines
        if line[0] != "{":
            continue
        # Eval results and store them
        flight_result = eval(line)
        dispersion_general_results.append(flight_result)
        for parameter_key, parameter_value in flight_result.items():
            dispersion_results[parameter_key].append(parameter_value)

    # Close data file
    dispersion_output_file.close()

    # Print number of flights simulated
    N = len(dispersion_general_results)
    print("Number of simulations: ", N)
    return dispersion_results

def outOfRailTime():
    dispersion_results = importMonteCarloResults()
    N = len(dispersion_results)
    print(f'Out of Rail Time - Mean Value: {np.mean(dispersion_results["out_of_rail_time"]):0.3f} s')
    print(f'Out of Rail Time - Standard Deviation: {np.std(dispersion_results["out_of_rail_time"]):0.3f} s')

    plt.figure()
    plt.hist(dispersion_results["out_of_rail_time"], bins=int(20))
    plt.title("Out of Rail Time")
    plt.xlabel("Time (s)")
    plt.ylabel("Number of Occurences")
    plt.show()

def outOfRailVelocity():
    dispersion_results = importMonteCarloResults()
    N = len(dispersion_results)
    print(f'Out of Rail Velocity - Mean Value: {np.mean(dispersion_results["out_of_rail_velocity"]):0.3f} m/s')
    print(f'Out of Rail Velocity - Standard Deviation: {np.std(dispersion_results["out_of_rail_velocity"]):0.3f} m/s')

    plt.figure()
    plt.hist(dispersion_results["out_of_rail_velocity"], bins=int(20))
    plt.title("Out of Rail Velocity")
    plt.xlabel("Velocity (m/s)")
    plt.ylabel("Number of Occurences")
    plt.show()
    
def timeToApogee():
    dispersion_results = importMonteCarloResults()
    N = len(dispersion_results)
    print(f'Apogee Time - Mean Value: {np.mean(dispersion_results["apogee_time"]):0.3f} s')
    print(f'Apogee Time - Standard Deviation: {np.std(dispersion_results["apogee_time"]):0.3f} s')

    plt.figure()
    plt.hist(dispersion_results["apogee_time"], bins=int(20))
    plt.title("Apogee Time")
    plt.xlabel("Time (s)")
    plt.ylabel("Number of Occurences")
    plt.show()
    
def apogeeAltitude():
    dispersion_results = importMonteCarloResults()
    N = len(dispersion_results)
    print(f'Apogee Altitude - Mean Value: {np.mean(dispersion_results["apogee_altitude"]):0.3f} m')
    print(f'Apogee Altitude - Standard Deviation: {np.std(dispersion_results["apogee_altitude"]):0.3f} m')

    plt.figure()
    plt.hist(dispersion_results["apogee_altitude"], bins=int(20))
    plt.title("Apogee Altitude")
    plt.xlabel("Altitude (m)")
    plt.ylabel("Number of Occurences")
    plt.show()

def apogeeXPosition():
    dispersion_results = importMonteCarloResults()
    N = len(dispersion_results)
    print(f'Apogee X Position - Mean Value: {np.mean(dispersion_results["apogee_x"]):0.3f} m')
    print(f'Apogee X Position - Standard Deviation: {np.std(dispersion_results["apogee_x"]):0.3f} m')

    plt.figure()
    plt.hist(dispersion_results["apogee_x"], bins=int(20))
    plt.title("Apogee X Position")
    plt.xlabel("Apogee X Position (m)")
    plt.ylabel("Number of Occurences")
    plt.show()
    
def apogeeYPosition():
    dispersion_results = importMonteCarloResults()
    N = len(dispersion_results)
    print(f'Apogee Y Position - Mean Value: {np.mean(dispersion_results["apogee_y"]):0.3f} m')
    print(f'Apogee Y Position - Standard Deviation: {np.std(dispersion_results["apogee_y"]):0.3f} m')

    plt.figure()
    plt.hist(dispersion_results["apogee_y"], bins=int(20))
    plt.title("Apogee Y Position")
    plt.xlabel("Apogee Y Position (m)")
    plt.ylabel("Number of Occurences")
    plt.show()
    
def impactTime():
    dispersion_results = importMonteCarloResults()
    N = len(dispersion_results)
    print(f'Apogee Y Position - Mean Value: {np.mean(dispersion_results["impact_time"]):0.3f} m')
    print(f'Apogee Y Position - Standard Deviation: {np.std(dispersion_results["impact_time"]):0.3f} m')

    plt.figure()
    plt.hist(dispersion_results["impact_time"], bins=int(20))
    plt.title("Impact Time")
    plt.xlabel("Time (s)")
    plt.ylabel("Number of Occurences")
    plt.show()

def impactXPosition():    
    dispersion_results = importMonteCarloResults()
    N = len(dispersion_results)    
    print(f'Impact X Position - Mean Value: {np.mean(dispersion_results["impact_x"]):0.3f} m')
    print(f'Impact X Position - Standard Deviation: {np.std(dispersion_results["impact_x"]):0.3f} m')

    plt.figure()
    plt.hist(dispersion_results["impact_x"], bins=int(20))
    plt.title("Impact X Position")
    plt.xlabel("Impact X Position (m)")
    plt.ylabel("Number of Occurences")
    plt.show()

def impactYPosition():    
    dispersion_results = importMonteCarloResults()
    N = len(dispersion_results) 
    print(f'Impact Y Position - Mean Value: {np.mean(dispersion_results["impact_y"]):0.3f} m')
    print(f'Impact Y Position - Standard Deviation: {np.std(dispersion_results["impact_y"]):0.3f} m')

    plt.figure()
    plt.hist(dispersion_results["impact_y"], bins=int(20))
    plt.title("Impact Y Position")
    plt.xlabel("Impact Y Position (m)")
    plt.ylabel("Number of Occurences")
    plt.show()
    
def impactVelocity():
    dispersion_results = importMonteCarloResults()
    N = len(dispersion_results) 
    print(f'Impact Velocity - Mean Value: {np.mean(dispersion_results["impact_velocity"]):0.3f} m/s')
    print(f'Impact Velocity - Standard Deviation: {np.std(dispersion_results["impact_velocity"]):0.3f} m/s')

    plt.figure()
    plt.hist(dispersion_results["impact_velocity"], bins=int(20))
    plt.title("Impact Velocity")
    plt.grid()
    plt.xlim(-35, 0)
    plt.xlabel("Velocity (m/s)")
    plt.ylabel("Number of Occurences")
    plt.show()
    
def staticMargin():
    dispersion_results = importMonteCarloResults()
    N = len(dispersion_results)
    print(f'Initial Static Margin - Mean Value: {np.mean(dispersion_results["initial_static_margin"]):0.3f} c')
    print(f'Initial Static Margin - Standard Deviation: {np.std(dispersion_results["initial_static_margin"]):0.3f} c')
    print(f'Out of Rail Static Margin - Mean Value: {np.mean(dispersion_results["out_of_rail_static_margin"]):0.3f} c')
    print(f'Out of Rail Static Margin - Standard Deviation: {np.std(dispersion_results["out_of_rail_static_margin"]):0.3f} c')
    print(f'Final Static Margin - Mean Value: {np.mean(dispersion_results["final_static_margin"]):0.3f} c')
    print(f'Final Static Margin -       Standard Deviation: {np.std(dispersion_results["final_static_margin"]):0.3f} c')

    plt.figure()
    plt.hist(dispersion_results["initial_static_margin"], label="Initial", bins=int(20))
    plt.hist(
        dispersion_results["out_of_rail_static_margin"],
        label="Out of Rail",
        bins=int(20),
    )
    plt.hist(dispersion_results["final_static_margin"], label="Final", bins=int(20))
    plt.legend()
    plt.title("Static Margin")
    plt.xlabel("Static Margin (c)")
    plt.ylabel("Number of Occurences")
    plt.show()

def errorEllipses(number_of_points):
    # Import background map
    img = imread(str(RESOURCE_DIR / "10kmX10kmBackground.jpg"))
    
    dispersion_results = importMonteCarloResults()
    # Check that the number of points is less than the size of the dispersion results
    if number_of_points > len(dispersion_results["apogee_x"]):
        raise ValueError("The number of points must be less than the size of the dataset")

    # Retrieve dispersion data por apogee and impact XY position
    apogee_x = np.array(dispersion_results["apogee_x"])[:number_of_points]
    apogee_y = np.array(dispersion_results["apogee_y"])[:number_of_points]
    impact_x = np.array(dispersion_results["impact_x"])[:number_of_points]
    impact_y = np.array(dispersion_results["impact_y"])[:number_of_points]


    # Define function to calculate eigen values
    def eigsorted(cov):
        vals, vecs = np.linalg.eigh(cov)
        order = vals.argsort()[::-1]
        return vals[order], vecs[:, order]


    # Create plot figure
    plt.figure(num=None, figsize=(8, 6), dpi=150, facecolor="w", edgecolor="k")
    ax = plt.subplot(111)

    # Calculate error ellipses for impact
    impactCov = np.cov(impact_x, impact_y)
    impactVals, impactVecs = eigsorted(impactCov)
    impactTheta = np.degrees(np.arctan2(*impactVecs[:, 0][::-1]))
    impactW, impactH = 2 * np.sqrt(impactVals)

    # Draw error ellipses for impact
    impact_ellipses = []
    for j in [1, 2, 3]:
        impactEll = Ellipse(
            xy=(np.mean(impact_x), np.mean(impact_y)),
            width=impactW * j,
            height=impactH * j,
            angle=impactTheta,
            color="black",
        )
        impactEll.set_facecolor((0, 0, 1, 0.2))
        impact_ellipses.append(impactEll)
        ax.add_artist(impactEll)

    # Calculate error ellipses for apogee
    apogeeCov = np.cov(apogee_x, apogee_y)
    apogeeVals, apogeeVecs = eigsorted(apogeeCov)
    apogeeTheta = np.degrees(np.arctan2(*apogeeVecs[:, 0][::-1]))
    apogeeW, apogeeH = 2 * np.sqrt(apogeeVals)

    # Draw error ellipses for apogee
    for j in [1, 2, 3]:
        apogeeEll = Ellipse(
            xy=(np.mean(apogee_x), np.mean(apogee_y)),
            width=apogeeW * j,
            height=apogeeH * j,
            angle=apogeeTheta,
            color="black",
        )
        apogeeEll.set_facecolor((0, 1, 0, 0.2))
        ax.add_artist(apogeeEll)

    # Draw launch point
    plt.scatter(0, 0, s=30, marker="*", color="black", label="Launch Point")
    # Draw apogee points
    plt.scatter(
        apogee_x, apogee_y, s=5, marker="^", color="green", label="Simulated Apogee"
    )
    # Draw impact points
    plt.scatter(
        impact_x, impact_y, s=5, marker="v", color="blue", label="Simulated Landing Point"
    )

    plt.legend()

    # Add title and labels to plot
    ax.set_title(
        "1$\sigma$, 2$\sigma$ and 3$\sigma$ Dispersion Ellipses: Apogee and Landing Points"
    )
    ax.set_ylabel("North (m)")
    ax.set_xlabel("East (m)")

    # Add background image to plot
    # You can translate the basemap by changing dx and dy (in meters)
    dx = 0
    dy = 0
    plt.imshow(img, zorder=0, extent=[-5000, 5000, -5000, 5000])
    plt.axhline(0, color="black", linewidth=0.5)
    plt.axvline(0, color="black", linewidth=0.5)
    plt.xlim(-5000, 5000)
    plt.ylim(-5000, 5000)

    # Show result
    plt.show()
