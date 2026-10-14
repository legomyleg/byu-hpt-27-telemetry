from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from rocketpy import Environment


def returnWindyEnvironment() -> Environment:
    ''' Generates a Windy environment with expected wind
    and pressure conditions of tomorrow
    '''

    windy_environment_Spaceport = Environment(latitude=32.94103529050622,
                                              longitude=-106.92203686488024,
                                              elevation=1385)

    # Choose Date for Simulation
    tomorrow = datetime.now(ZoneInfo("America/Denver")) + timedelta(days=1)

    windy_environment_Spaceport.set_date(
        (tomorrow.year, tomorrow.month, tomorrow.day, 12)
    )  # Hour given in UTC time

    # Set Atmospheric Model Type and Height
    windy_environment_Spaceport.process_windy_atmosphere(model="ECMWF")
    windy_environment_Spaceport.set_atmospheric_model(type="Windy",
                                                      file="ECMWF")
    windy_environment_Spaceport.max_expected_height = 12000
    return windy_environment_Spaceport


# Print out information
def printWindyEnvironment():
    windy_environment_Spaceport = returnWindyEnvironment()
    return windy_environment_Spaceport.all_info()


def returnConstantEnvironment() -> Environment:
    ''' Generates a constant environment with a pressure,
    temperature, and windspeed equal to the environmental
    factors seen at Spaceport 2024.
    '''
    constant_wind_Spaceport = Environment(latitude=32.990254,
                                          longitude=-106.974998,
                                          elevation=1385)

    constant_wind_Spaceport.max_expected_height = 15000
    # Choose Date for Simulation
    tomorrow = datetime.now(ZoneInfo("America/Denver")) + timedelta(days=1)

    constant_wind_Spaceport.set_date(
        (tomorrow.year, tomorrow.month, tomorrow.day, 12)
    )  # Hour given in UTC time

    constant_wind_Spaceport.set_atmospheric_model(type="custom_atmosphere",
                                                  pressure=101321,
                                                  temperature=304.26,
                                                  wind_u=5,
                                                  wind_v=5)
    return constant_wind_Spaceport


def printConstantEnvironment():
    constant_wind_Spaceport = returnConstantEnvironment()
    return constant_wind_Spaceport.all_info()
