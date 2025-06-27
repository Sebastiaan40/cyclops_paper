# Abstract

Rotational activity is one of the mechanisms behind cardiac arrhythmias,
and it is therefore important to accurately localize such activity in cardiac tissue.
A standard method for this, is called phasemapping.
While widely used for analysing rotors in cardiac simulations,
phasemapping struggles to correctly analyse activation maps with large non-conductive regions
and/or conductive blocks.
To illustrate these, we examine a simulation that exhibits these treats,
and demonstrate how each of them can be addressed.

# Introduction

**Action**

- Introduce the simulation
- Refer to analysis with standard phasemapping
- Refer to analysis using extended phasemapping --> curiosity

**Background (research topic, niche, problem, solution, introdcution to methods)**

- Make problems with the simulation concrete
- Explain that these are common in clinical cases
- Introduce the solution

**Development**

# Methods

- What is phase?
- The phase index and its properties
- Standard phasemapping method
- Simulation

**Climax**

# Results

- First step: standard method
- Second step: removing edges that go through phase defects
- Third step: going around phase defects

# Discussion

- Showcase clinical relevance.
- Limitations: simulation instead of clinical case, phase is necessary to know
  --> We can use the signals or LATs if needed
- Paper arno2023 --> even more impractical for clinical cases
- Growth and shrinking is irrelevant for AT (although functional block is temporal)
- Paper kabus2024 --> phase definitions, sawtooth
- Limitations: identifying phase defects
- Paper arno2024
- Limitations: noisy data
- Finite wavelength could give an additional requirement which can limit false positives
- Paper of different phasemapping thresholds might be explained by phase defects
- Comparison with different methods (back-tracking, intersection points)
  --> back-tracking cannot find near-complete rotations
  --> intersection points are the same as phasemapping

**Ending**

# Conclusion

- Properly addressing phasedefects and adapting the curve can make phasemapping
  suitable for analysing clinical cases. Refer to preregistration.
