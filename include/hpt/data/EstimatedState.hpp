#pragma once

namespace hpt::data {

struct Position {
    double latitude;
    double longitude;
    double altitude_asl;
};

struct VelocityENU {
    float east_mps;
    float north_mps;
    float up_mps;
};

struct Attitude {
    float w;
    float x;
    float y;
    float z;
};

struct AngularVelocity {
    float x;
    float y;
    float z;
};

struct EstimatedState {
    Position position;
    VelocityENU velocity_enu;
    Attitude attitude_body_to_enu;
    AngularVelocity angular_velocity_body_rad_s;
};

}
