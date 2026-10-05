#define DOCTEST_CONFIG_IMPLEMENT_WITH_MAIN
#include <doctest/doctest.h>
#include "hpt/data/SensorSample.hpp"
#include <vector>

std::vector<int> findNonIncreasingSamples(
    const std::vector<hpt::data::SensorSample>& samples
);

TEST_CASE("empty input returns no bad indices"){
    std::vector<hpt::data::SensorSample> samples;
    auto result = findNonIncreasingSamples(samples);
    CHECK(result.empty());
}

TEST_CASE("one input is handled correctly"){
    std::vector<hpt::data::SensorSample> samples = {
        {std::chrono::microseconds(100), 0, 0, 0, 0}
    };
    auto result = findNonIncreasingSamples(samples);
    CHECK(result.empty());
}

TEST_CASE("increasing timestamps success"){
    std::vector<hpt::data::SensorSample> samples = {
        {std::chrono::microseconds(100), 0, 0, 0, 0},
        {std::chrono::microseconds(200), 0, 0, 0, 0},
        {std::chrono::microseconds(300), 0, 0, 0, 0},
        {std::chrono::microseconds(400), 0, 0, 0, 0}
    };
    auto result = findNonIncreasingSamples(samples);
    CHECK(result.empty());
}

TEST_CASE("one late sample testing"){
    std::vector<hpt::data::SensorSample> samples = {
        {std::chrono::microseconds(100), 0, 0, 0, 0},
        {std::chrono::microseconds(200), 0, 0, 0, 0},
        {std::chrono::microseconds(150), 0, 0, 0, 0},
        {std::chrono::microseconds(400), 0, 0, 0, 0}
    };
    auto result = findNonIncreasingSamples(samples);
    CHECK(result == std::vector<int>{2});
}

TEST_CASE("consecutive late samples"){
    std::vector<hpt::data::SensorSample> samples = {
        {std::chrono::microseconds(100), 0, 0, 0, 0},
        {std::chrono::microseconds(150), 0, 0, 0, 0},
        {std::chrono::microseconds(130), 0, 0, 0, 0},
        {std::chrono::microseconds(120), 0, 0, 0, 0}
    };
    auto result = findNonIncreasingSamples(samples);
    CHECK(result == std::vector<int>{2,3});
}


TEST_CASE("decreasing timestamps test"){
    std::vector<hpt::data::SensorSample> samples = {
        {std::chrono::microseconds(100), 0, 0, 0, 0},
        {std::chrono::microseconds(90), 0, 0, 0, 0},
        {std::chrono::microseconds(80), 0, 0, 0, 0},
        {std::chrono::microseconds(70), 0, 0, 0, 0}
    };
    auto result = findNonIncreasingSamples(samples);
    CHECK(result == std::vector<int>{1,2,3});
}


TEST_CASE("repeated maximum test"){
    std::vector<hpt::data::SensorSample> samples = {
        {std::chrono::microseconds(100), 0, 0, 0, 0},
        {std::chrono::microseconds(300), 0, 0, 0, 0},
        {std::chrono::microseconds(200), 0, 0, 0, 0},
        {std::chrono::microseconds(300), 0, 0, 0, 0},
        {std::chrono::microseconds(400), 0, 0, 0, 0}
    };
    auto result = findNonIncreasingSamples(samples);
    CHECK(result == std::vector<int>{2,3});
}
