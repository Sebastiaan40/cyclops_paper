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

A qualtative description of our methods is given below.
Readers who would like to reproduce our results are referred to this GitHub repository (LINK!!!).

1. Create the simulation using finitewave (CITE !!!), Aliev-Panfilov model. [@aliev1996a]
   The simulation should contain:

   - Two boundaries that are connected to each other with an unknown ablation line
   - A boundary that has a functional block attached to it

2. construct the phase field for the simulation from the u and v parameters
   (it might be better to construct it using a time delay so that no knowledge of the aliev panfilov model is needed)
   --> show a phasemap of a single cell

3. Standard phasemapping algorithm (look up summary paper of phasemapping)

4. Localize the phase defects by setting a threshold on the maximum difference of between neighboring phases.
   (check if this can be done analytically, what is the maximal difference at each time step?)

5. Repeat the standard phasemapping algorithm,
   but now all cycles that have a phase defect are removed
   and new cycles that surround the phase defects are added

**Climax**

# Results

- Add workflow diagram with both the standard and extended method
- First step: standard method
- Second step: removing edges that go through phase defects

# Discussion

- Showcase clinical relevance. [@duytschaever2024atrial, @santucci2024identification, @takigawa2019a]
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

- Properly addressing phase defects and adapting the curve can make phasemapping
  suitable for analysing clinical cases.
- Refer to preregistration.

This paper is meant to serve as a theoretical backbone to understand
how phasemapping can be used in a clinical setting.
Researcher who are interested in testing these ideas,
can have a look at our preregistration (LINK!!!).
