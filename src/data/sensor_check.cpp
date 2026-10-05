#include <hpt/data/SensorSample.hpp>
#include <vector>


std::vector<int> findNonIncreasingSamples(
    const std::vector<hpt::data::SensorSample>& samples){

        std::vector<int> bad_indices; //This is the vector that will store the indices of bad timestamps
        std::chrono::microseconds largest_timestamp;

        if (samples.empty()){
            return bad_indices;
        }
        largest_timestamp = samples[0].t_us;
        for (int i = 1; i < samples.size(); i++){
            std::chrono::microseconds current_timestamp = samples[i].t_us;
            if (current_timestamp > largest_timestamp){
                largest_timestamp = current_timestamp;
            }
            else {
                bad_indices.push_back(i);
            }
        }
        return bad_indices;
    }
