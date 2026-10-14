import json
from pathlib import Path
import Escalante
import SpaceportEnvironment as SE
from rocketpy import Flight

windyEnv = SE.returnWindyEnvironment()
constantEnv = SE.returnConstantEnvironment()
AeroTech_O5500X = Escalante.DefineMotor()
escalante = Escalante.DefineEscalante()

flight = Flight(
    rocket=escalante, environment=windyEnv, rail_length=5.2,
    inclination=84, heading=48.62, max_time=1200
)

solution = flight.solution_array

samples = []

for row in solution:
    t = float(row[0])

    samples.append({
        "timestamp": t,
        "latitude": float(flight.latitude(t)),
        "longitude": float(flight.longitude(t)),
        "altitude": float(row[3]),
        "qw": float(row[7]),
        "qx": float(row[8]),
        "qy": float(row[9]),
        "qz": float(row[10]),
    })

output_path = (
    Path(__file__).resolve().parents[2]
    / "resources" / "sim_data" / "rocketpy_data.json"
)
output_path.parent.mkdir(parents=True, exist_ok=True)

with output_path.open("w", encoding="utf-8") as output:
    json.dump(samples, output, indent=2, allow_nan=False)
