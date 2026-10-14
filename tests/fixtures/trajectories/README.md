# Reusable trajectories

Keep these recorded snapshots stable for repeatable replay and tests. New
RocketPy runs write to `resources/sim_data/`; they do not overwrite these files.
No automated test currently consumes these snapshots.

| File | Format | Samples | Simulation time range (seconds) |
| --- | --- | --- | --- |
| `escalante_spaceport_geodetic.json` | Array of geodetic position and attitude records | 1693 | 0 to 87.02678295713403 |
| `escalante_state_vector_legacy.csv` | Native RocketPy state vector rows | 1583 | 0 to 86.79584092135796 |

These are two different existing recordings, not JSON and CSV exports of the
same flight. Their original simulation dates, weather snapshots, and dependency
versions were not recorded. Do not assume rerunning the current scripts will
reproduce them.

## JSON fields

- `timestamp`: simulation time in seconds.
- `latitude`, `longitude`: decimal degrees, positive north/east.
- `altitude`: meters above sea level.
- `qw`, `qx`, `qy`, `qz`: unitless scalar-first RocketPy body-to-ENU quaternion.

The initial latitude and longitude are 32.94103529050622 and
-106.92203686488024, respectively. The initial altitude is 1371 meters.

## CSV fields

The header is `t,x,y,z,vx,vy,vz,e0,e1,e2,e3,omega1,omega2,omega3`.

- `t`: simulation time in seconds.
- `x`, `y`: east/north displacement from the launch point in meters.
- `z`: meters above sea level; the initial value is 1378 meters.
- `vx`, `vy`, `vz`: east/north/up velocity in meters per second.
- `e0`, `e1`, `e2`, `e3`: unitless scalar-first RocketPy quaternion.
- `omega1`, `omega2`, `omega3`: body angular velocity in radians per second.

The CSV does not record launch latitude or longitude. Keep it as a legacy
state-vector fixture rather than inferring geodetic coordinates from the JSON.
