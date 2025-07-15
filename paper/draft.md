---
title: The problem with standard phasemapping
author: Bjorn Verstraeten
date: \today
classoption: twocolumn
---

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

<!-- Adjust this to focus on cardiac modelers how use phasemapping. -->

Consider the following clinical case:
A patient suffers from atrial fibrillation and pulmonary vein isolation (PVI) is performed.
After PVI, the fibrillation converts to atrial tachycardia
and the patient is further treated by performing a roof ablation.
Therefore, the left and right pulmonary veins can be considered as one non-conductive region.
However, the tachycardia doesn't terminate
and in order to decide the next treatment step,
an activation map is made.

This activation map is shown in Figure (REF)
and by visually inspecting the map,
rotational activity can be identified around the mitral valve and the atrial roof.
We do not consider visual inspection as an optimal solution as it is subject to human mistakes.
Instead, it would much more preferable to have a tool
that would act as some kind of spell check where the error,
in this case the rotational activity, is highlighted.

A potential candidate for such tool is called phasemapping,
which will be discussed in the next section.
However, we will show that a standard implementation of phasemapping is not capable
of analysing a map with large non-conductive regions and/or conductive blocks,
such as the activation map described above.
And it is not because the idea behind phasemapping is lacking.
Rather, it's because the standard implementation mistreats such maps.

In this paper, we will summarize the idea behind phasemapping,
putting emphasis on the requirements for which the standard implementation gives the correct result.
We will then formally define conductive blocks and
showcase how to extend standard phasemapping
in order to treat conductive block and non-conductive regions properly.

# Theory

## What is the phase index?

<!-- Strogatz could give some inspiration on how to explain this better -->

When analyzing an electroanatomical map,
we often want to know if there is some rotational activity present,
since this is one of the mechanisms behind cardiac arrhythmia.
To express rotational activity a bit more quantitative,
we can state that, if there is a closed curve $C$ around which
the electrical excitation travels,
there is rotational activity across that curve.

We can get an even clearer expression
if we describe the state of each point at a certain time with a single variable.
Considering that the state of each point changes periodically,
the variable can be any scalar that is lying onto the unit circle.
This variable is referred to as the phase $\Phi$.

For a phase field $\Phi(x, t)$,
which describes the state of each point in a two-dimensional orientable manifold M (e.g. a plane or the surface of a sphere),
it hold that
if $\Phi$ is smooth across $C$,
and we follow $\Phi$ along $C$ until we end up back at the starting point,
The value will now be the same,
or it will be shifted by $2\pi$.
This expression can also be written down in a mathematical formula.

$$
2\pi I = \oint_C \nabla \Phi \cdot dl ,
$$

where $I$ is called the phase index of the curve.
Using Stokes' theorem,
the phase index can also be written as

$$
I = \frac{1}{2\pi} \iint_S \nabla \times (\nabla \Phi) \cdot dS
$$

In case $\Phi$ is differentiable across S,
the index $I$ is zero.
Which means that $I$ is only non-zero if a singular point is present in S. [@herlin2012reconstruction]
This singular point is exactly what a rotor tip or spiral core is being identified with.

## Properties of the phase index

The first thing we want you to notice,
is that the phase index is a property of a closed curve.
This can be any closed curve,
but for our purposes, we will stick to closed curves that do not intersect themselves.

<!-- Check out how davidsen and strogatz explain this -->

Secondly, since the phase index is an integer and the manifold is differentiable,
the curve can be continuously deformed without altering the phase index.
Therefore, the phase index is conserved for continuous deformations,
which is why it is called a topological charge.
This property allows us to identify a phase index to a singular point as follows:
The phase index of a singular point is the phase index of any closed curve that surrounds that point and nothing else.

<!-- Figure idea: draw multiple curves around a point -->

This idea can be generalized by stating that the phase index of a closed curve is equal to the total phase index of everything in that curve.
For example, if we draw a curve around multiple singular points $x_1$, ..., $x_N$,
the phase index $I_C$ of the curve is equal to that of the sum of the phase indices $I_n$ of all singular points inside.

$$
I_C = \sum^N_{n=1} I_n
$$

<!-- Figure idea: draw a curve around a multiple points -->

To build further on this idea,
suppose that we have defined a phase field $\Phi$ on a closed surface $S$.
If we now draw a curve on that surface with nothing in it,
its phase index will be zero.
Since $S$ is a closed surface,
this curve also encircles everything, and thus,
we can write

$$
\sum_{x_n \in S} I(x_n) = 0
$$

This is the same as stating that the total topological charge is conserved on a closed surface.

In order to extend this conservation law for surfaces with boundaries or holes
we can imagine to fill up these holes to get a closed surface
and use their boundaries as the closed curve to calculate the phase index.
For a more thorough explanation we refer to [@herlin2012reconstruction, @davidsen2004topological].
This extension then gives us the following equation:

$$
\sum_{x_n \in S} I(x_n) = \sum_{H_m \in S} I(H_m)
$$

where $x_n$ are the singular points in $S$ and $H_m$ are the holes.
From now on we will refer to this as the index theorem.

### How to handle conduction blocks or phase defects

So far we have defined the phase index for singular points and holes,
but now we need to remind ourselves about which requirements need to be fulfilled
in order to do so.
For our purposes, the most important one is that the phase field needs to be smooth across the closed curve.
One example where this is not fulfilled are singular points.
Another example that applies to cardiac tissue is when the wavefront of the excitation wave hits a refractory region.
This forms a discontinuity or defect in the form of a line.
A full discussion about this phenomena can be found in [@tomii2021spatial],
but for our purpose it is enough to define a phase defect as a discontinuity in the phase field.

## Detecting rotational activity in cardiac tissue

A well-known method that exploits the idea of phase indices is called phasemapping.
With phasemapping, the cardiac activation map is scanned across with a small area
and the phase index is computed along the circumference of this area.
Since method is mostly used while analysising rotors,
the scanning area is made as small as possible in order to ensure
that only one singular point lies within the area.

We argue that using phasemapping will give a incomplete analysis
because the cardiac can have phase defects and boundaries
for which the points that lie on them cannot be properly analysed using this method
Figure (LINK) shows that you cannot draw a closed curve soley around such points
that is smooth.
In other words, there is no way of analysing all points separatly and
the next best thing that we can do,
is calculating the phase index for the boundaries and the phase defect as a whole.

<!-- A curve should be as small as possible, but as big as necessary. -->

# Methods

There exists a numeruous amount implementations and methods to detect rotational activity [@pikunov2023th, @gurevich2019robuste, @li2020standardizing]
that it is almost impossible to create comparative study or full review.
Therefore, we have decided to create a case study.
We will analysis single simulation that contains boundaries and phase defects,
and simple enough to visually confirm.

## Setup of the Simulation

As it is not required to have realistic geometries to induce phase defects,
We chose to create a simulation on a homogeneous 2D grid.
This also has the benefit to get a full overview of the simulation at once
and easily place snapshots in the paper.

The simulation is created using Finitewave (<https://github.com/finitewave/Finitewave>),
an open-source Python package for a wide range of tasks in modeling cardiac electrophysiology using finite-difference methods.
The main argument for using Finitewave is its clear and transparent implementation of the models
which allows us to verify its correctness.
Furthermore, the intuitive interface and lots of examples make it easy to create, evaluate, and adjust simulations.

The cell model used for the simulation is the Fenton-Karma model.
Since the research question of this paper does not involve the effect of ionic channels on the dynamics,
it is more fitting to use a phenomenological model which is less computationally heavy
and has simpler cell dynamics.
We choose the Fenton-Karma model specifically since it was the easiest to create phase defects without tweaking the model's parameters.

The 2D mesh is first pre-paced with 10 planar stimuli and an interval of 200 time steps between them.
Next, a boundary is added inside the mesh
and a second square stimulus is applied to induce rotational activity.
To ensure that the rotor fits on the mesh, but without increasing computational time,
we lowered the conductivity of the mesh.
Finally, we added a phase defect using a third stimulus in a small region just before it goes out of refractory.

## Implementation of phasemapping

To highlight the influence of phase defects and boundaries,
we will compare two implementations of phasemapping:
one where the simulation is scanned for singularities without adresing phase defects and ignoring boundaries,
and another were we take into account phase defects and boundaries.
This second implementation is basically an extension of the first one.

## Naive Phasemapping

2. construct the phase field for the simulation from the u and v parameters
   Using Hilbert transform since this corresponds phase rotation [@bray2002considerations]
   --> show a phasemap of a single cell

3. Standard phasemapping algorithm (look up summary paper of phasemapping)

## Extended phasemapping

4. Localize the phase defects by setting a threshold on the maximum difference of between neighboring phases.
   (check if this can be done analytically, what is the maximal difference at each time step?)

5. Repeat the standard phasemapping algorithm,
   but now all cycles that have a phase defect are removed
   and new cycles that surround the phase defects are added

Readers who would like to reproduce our results are referred to this GitHub repository (LINK!!!),
which contains the used code and some further explanation.

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
- Limitation: while defining a phase defect as a discontinuity is fine,
  it does not tell the whole story. For example, looking at the fork,
  the discontinuity disappears when the wavefront is moving away from it.
  However, the next wave still can't pass through it.

Besides phasemapping, there exists other methods such as:

Since the phase space of cardiac tissue can exhibit interfaces or defects,
it is not necessarily guaranteed that phasemapping and waveback -and front intersection points give the correct analysis.
This could explain the reason why using different thresholds to count phase jumps,
gives different results. (LINK!!!)

For backtracking, phase defects are not a problem, as it will inherently go around them.
However, this method is probably incapable of detecting near-complete rotations.

Equivalent to topological charges, we could also count the number of [phase jumps]().

<!-- might be wrong since they don't integrate -->

The kernel method requires that the full region is smooth,
which means that it cannot calculate the phase index over phase defects.

**Ending**

# Conclusion

- Properly addressing phase defects and adapting the curve can make phasemapping
  suitable for analysing clinical cases.
- Refer to preregistration.
- Additionaly, we encourage research groups to try out this simple example
  to see whether their detection method can analyse this map correctly.
  However, keep in mind Goodhart's Law

This paper is meant to serve as a theoretical backbone to understand
how phasemapping can be used in a clinical setting.
Researcher who are interested in testing these ideas,
can have a look at our preregistration (LINK!!!).
