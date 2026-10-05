#pragma once
#include <chrono>
#include <hpt/data/Vec3.hpp>

namespace hpt::data {

struct InertialData {
    std::chrono::microseconds t_us;

    Vec3f accel_mps2{};
    Vec3f gyro_radps{};
    Vec3f high_g_accel_mps2{};
};

}
