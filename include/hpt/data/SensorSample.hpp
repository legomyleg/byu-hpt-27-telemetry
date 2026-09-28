#pragma once
#include <chrono>

namespace hpt::data {
    
struct SensorSample {
    std::chrono::microseconds t_us;
    float accel_x;
    float accel_y;
    float accel_z;
    float baro;
};

}
