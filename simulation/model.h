#pragma once
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace lab
{
struct Config
{
    std::string protocol = "deadline_aware", topology = "diamond", mobility = "static",
                traffic = "constant", output = "results/raw/manual", rateMode = "OfdmRate6Mbps";
    uint32_t nodes = 4, seed = 1, run = 1, payload = 256, queueCapacity = 32, maxHops = 32,
             flows = 1;
    double duration = 5, start = 1, stop = 4, rate = 20, spacing = 80, area = 400, range = 125,
           power = 30, pathLoss = 3, speed = 5, pause = 0.2;
    double processing = 1, slowProcessing = 30, minHoldoff = 0.5, maxHoldoff = 5, safety = 0.5,
           perHop = 3, hello = 0.1;
    double diamondHeight = 20;
    double deadline = 0, loss = 0;
    uint32_t lossNode = UINT32_MAX;
    std::array<double, 4> deadlines{50, 100, 500, 1000}, mix{0.25, 0.25, 0.25, 0.25},
        weights{0.3, 0.3, 0.3, 0.1};
    std::vector<std::pair<uint32_t, uint32_t>> pairs;

    void Validate() const
    {
        auto one = [](auto s, auto choices) {
            return choices.find("|" + s + "|") != std::string::npos;
        };
        if (!one(protocol, std::string("|fixed|opportunistic|deadline_aware|")) ||
            !one(topology, std::string("|diamond|line|grid|random|mobile|")) ||
            !one(mobility, std::string("|static|waypoint|velocity|")) ||
            !one(traffic, std::string("|constant|poisson|")))
        {
            throw std::runtime_error("Unknown protocol, topology, mobility or traffic model");
        }
        if (nodes < 2 || nodes > 500 || (topology == "diamond" && nodes != 4) || flows == 0 ||
            flows >= nodes || !seed || !run || payload < 1 || payload > 1400 || !queueCapacity ||
            !maxHops || maxHops > 65535)
        {
            throw std::runtime_error("Invalid nodes/flows/seed/payload/queue/hop limit");
        }
        for (double v :
             {duration,   start,    stop,   rate,  spacing,    area,           range,
              power,      pathLoss, speed,  pause, processing, slowProcessing, minHoldoff,
              maxHoldoff, safety,   perHop, hello, deadline,   loss,           diamondHeight})
        {
            if (!std::isfinite(v))
            {
                throw std::runtime_error("Non-finite parameter");
            }
        }
        if (start < 0 || stop <= start || duration <= stop || rate <= 0 || rate > 100000 ||
            spacing <= 0 || area <= 0 || range <= 0 || pathLoss <= 0 || speed < 0 || pause < 0 ||
            processing < 0 || slowProcessing < 0 || minHoldoff < 0 || maxHoldoff < minHoldoff ||
            safety < 0 || perHop <= 0 || hello <= 0 || deadline < 0 || diamondHeight < 0 ||
            loss < 0 || loss > 1)
        {
            throw std::runtime_error("Invalid timing/radio/traffic bounds");
        }
        for (const auto& a : {weights, mix})
        {
            double sum = 0;
            for (double v : a)
            {
                if (!std::isfinite(v) || v < 0)
                {
                    throw std::runtime_error("Weights/proportions must be finite and nonnegative");
                }
                sum += v;
            }
            if (std::abs(sum - 1) > 1e-6)
            {
                throw std::runtime_error("Weights/proportions must sum to one");
            }
        }
        for (double d : deadlines)
        {
            if (!std::isfinite(d) || d <= 0)
            {
                throw std::runtime_error("Deadlines must be positive");
            }
        }
        for (auto [s, d] : pairs)
        {
            if (s >= nodes || d >= nodes || s == d)
            {
                throw std::runtime_error("Invalid source-destination pair");
            }
        }
    }
};

struct Decision
{
    double score = 0, link = 0, progress = 0, estimate = 0, wait = 0, queueDelay = 0, slack = 0;
    bool eligible = false;
    std::string reason;
};

inline Decision
Select(const Config& c,
       double quality,
       double progress,
       double distance,
       double queueDelay,
       double processing,
       double remaining)
{
    Decision d;
    d.link = std::clamp(quality, 0., 1.);
    d.progress = std::clamp(progress / c.range, 0., 1.);
    d.queueDelay = queueDelay;
    double basic = .5 * d.link + .5 * d.progress;
    // Rank with slack before contention, then test feasibility with the resulting actual holdoff.
    d.estimate = processing + queueDelay + std::ceil(distance / c.range) * c.perHop;
    d.slack = remaining - d.estimate - c.safety;
    d.score = c.protocol == "deadline_aware"
                  ? c.weights[0] * d.link + c.weights[1] * d.progress +
                        c.weights[2] * std::clamp(d.slack / std::max(remaining, 1e-9), 0., 1.) +
                        c.weights[3] / (1 + queueDelay / std::max(processing, 0.1))
                  : basic;
    d.wait = c.minHoldoff + (1 - d.score) * (c.maxHoldoff - c.minHoldoff);
    d.estimate += d.wait;
    d.slack = remaining - d.estimate - c.safety;
    d.eligible = progress > 0 && (c.protocol != "deadline_aware" || d.slack > 0);
    d.reason = progress <= 0 ? "NO_PROGRESS" : (!d.eligible ? "DEADLINE_INFEASIBLE" : "");
    return d;
}
} // namespace lab
