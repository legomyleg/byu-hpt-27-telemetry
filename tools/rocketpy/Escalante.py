from pathlib import Path

from rocketpy import SolidMotor, Rocket


RESOURCE_DIR = Path(__file__).resolve().parents[2] / "resources" / "rocketpy"


def DefineMotor():
    ''' Import all of the Motor Information for the AeroTech_O5500X
    '''
    AeroTech_O5500X = SolidMotor(
        thrust_source=str(RESOURCE_DIR / "AeroTech_O5500X-PS.eng"),
        dry_mass=7.004,
        dry_inertia=(1.329, 1.329, 0.002),
        nozzle_radius=40 / 1000,
        grain_number=1,
        grain_density=1474,
        grain_outer_radius=43 / 1000,
        grain_initial_inner_radius=15 / 1000,
        grain_initial_height=1300 / 1000,
        grain_separation=1 / 1000,
        grains_center_of_mass_position=0.753,
        center_of_dry_mass_position=0.753,
        nozzle_position=0,
        burn_time=3.997,
        throat_radius=15 / 1000,
        coordinate_system_orientation="nozzle_to_combustion_chamber",
    )
    return AeroTech_O5500X


def PrintMotorDetails():
    ''' Return all of the details of the motor
    '''
    AeroTech_O5500X = DefineMotor()
    return AeroTech_O5500X.all_info()


def DefineEscalante():
    AeroTech_O5500X = DefineMotor()

    escalantev21 = Rocket(
        radius=78 / 1000,
        mass=18.087,
        inertia=(7.5811, 7.5811, 0.109),
        power_off_drag=str(RESOURCE_DIR / "Escalante 30k v2.1cdpoweroff.CSV"),
        power_on_drag=str(RESOURCE_DIR / "Escalante 30k v2.1cdpoweron.CSV"),
        center_of_mass_without_motor=-1.2504674,
        coordinate_system_orientation="tail_to_nose",
    )

    escalantev21.set_rail_buttons(
        upper_button_position=-2.4892,
        lower_button_position=-2.794,
        angular_position=45,
    )

    escalantev21.add_motor(AeroTech_O5500X, position=-3.0509)
    escalantev21.add_nose(length=0.673, kind="ogive", position=0)

    escalantev21.add_trapezoidal_fins(
        n=4,
        root_chord=0.203,
        tip_chord=0.061,
        span=0.13,
        position=-2.694,
        cant_angle=0,
        sweep_length=.203,
        airfoil=(str(RESOURCE_DIR / "NACA0012-radians.csv"), "radians")
    )

    escalantev21.add_tail(
        top_radius=0.078, bottom_radius=0.0711, length=0.051, position=-2.899
    )
    escalantev21.add_tail(
        top_radius=0.0711, bottom_radius=0.064, length=0.1, position=-3.0285
    )
    escalantev21.add_tail(
        top_radius=0.064, bottom_radius=0.0535, length=0.013, position=-3.1285
    )

    return escalantev21


def addParachutes():
    rocket = DefineEscalante()
    rocket.add_parachute(
        "Main",
        cd_s=10.273,
        trigger=1500,
        sampling_rate=105,
        lag=1.5,
        noise=(0, 8.3, 0.5),
    )

    rocket.add_parachute(
        "Drogue",
        cd_s=0.5253543144,
        trigger="apogee",
        sampling_rate=105,
        lag=1.5,
        noise=(0, 8.3, 0.5),
    )
    return rocket


def removeParachutes(rocket: Rocket):
    rocket.parachutes.clear()


def PrintEscalante():
    escalantev21 = addParachutes()
    return escalantev21.all_info()

