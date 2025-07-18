---
title: How phase defects and boundaries can mess up phasemapping
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

Consider the simulation in Figure~LINK.
By visually inspecting the map,
a linear rotor appears to turn counterclockwise in the bottom left [@arno2021a].
Looking at the bottom right,
you can see two wavefronts soon to collide with each other.
At the top we find a more complex pattern.
There is a non-conductive region around which three wavefronts are moving.
One might recognize this pattern as a critical boundary with near-complete rotation;
a pattern that plays an important role during ablation therapy [@duytschaever2024atrial, @santucci2024identification].

While for this simple simulation, a visual inspection is reasonable,
it is not considered as an optimal solution as it is subject to human mistakes.
Instead, it would much more preferable to have a tool
that would act as some kind of spell check where the error,
in this case the rotational activity, is highlighted.

A potential candidate for such tool is called phasemapping,
which will be discussed in the next section.
However, we will show that a naive implementation of phasemapping is not capable
of analysing a map with large non-conductive regions and/or conductive blocks,
such as the phase map described above.
And it is not because the idea behind phasemapping is lacking.
Rather, it's because a naive approach mistreats such maps.

In this paper, we will summarize the idea behind phasemapping,
putting emphasis on the requirements for which the standard implementation gives the correct result.
We will then formally define conductive blocks and
showcase how to extend standard phasemapping
in order to treat conductive block and non-conductive regions properly.

![Snapshot of a simulation with the Fenton-Karma model that contains discontinuities and holes.
An analysis is done with a naive implementation of phasemapping (left) and with the proposed approach (right).
The values of the mesh correspond the phase field, of which a value of $\pi$ corresponds with the excitation wavefront.
Discontinuities, boundaries and rotors are annotated with red if a counterclockwise rotation is found and in blue for clockwise rotation.
Discontinuities and boundaries that do not show any rotation are annotated in white.](paper/figures/comparison_snapshot_overview.png)

# Theory

<!-- Is this part redundant. Should it be made smaller? -->

## What is the phase index?

<!-- Strogatz could give some inspiration on how to explain this better -->

When analysing an electro-anatomical map,
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
it holds that
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

This idea can be generalized by stating that the phase index of a closed curve is equal to the total phase index of everything in that curve.
For example, if we draw a curve around multiple singular points $x_1$, ..., $x_N$,
the phase index $I_C$ of the curve is equal to that of the sum of the phase indices $I_n$ of all singular points inside.

$$
I_C = \sum^N_{n=1} I_n
$$

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
A full discussion about this phenomenon can be found in [@tomii2021spatial],
but for our purpose it is enough to define a phase defect as a discontinuity in the phase field.

Figure~LINK show an example on how to adjust the curves when phase defects and holes are present.

![Example of a bounded planar domain with holes.
The domain contains singular points at $\pmb{x}_1$, ..., $\pmb{x}_n$
and holes $H_1$, ... $H_{m-1}$, with the outer boundary representing the final hole $H_m$.
Curves are drawn around each singular point and hole with the arrow represent the direction of integration.
In addition, a phase defect is presented together with a curve over which to integrate to get the phase index of the defect.](paper/figures/index_calculation.pdf)

## Detecting rotational activity in cardiac tissue

A well-known method that exploits the idea of phase indices is called phasemapping.
With phasemapping, the cardiac activation map is scanned across with a small area
and the phase index is computed along the circumference of this area.
Since this method is mostly used while analysing rotors,
the scanning area is made as small as possible in order to ensure
that only one singular point lies within the area.

We argue that using phasemapping will give an incomplete analysis
because the cardiac can have phase defects and boundaries
for which the points that lie on them cannot be properly analysed using this method
Figure (LINK) shows that you cannot draw a closed curve solely around such points
that is smooth.
In other words, there is no way of analysing all points separately and
the next best thing that we can do,
is calculating the phase index for the boundaries and the phase defect as a whole.

<!-- A curve should be as small as possible, but as big as necessary. -->

# Methods

<!-- Use the original papers that propose the algorithms instead of li2020standardizing -->

There exists a numerous amount implementations and methods to detect rotational activity [@pikunov2023th, @gurevich2019robuste, @li2020standardizing]
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
an open-source Python package for a wide range of tasks in modelling cardiac electrophysiology using finite-difference methods.
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
one where the simulation is scanned for singularities without addressing phase defects and ignoring boundaries,
which we will refer to as naive phasemapping,
and another were we take into account phase defects and boundaries.
This second implementation is basically an extension of the first one,
so we will refer to it as extended phasemapping.

## Naive Phasemapping

The first step was to convert the action potential to a phase field.
This was done using taking the angle Hilbert transform of the action potential as suggested by [@bray2002considerations].
Additionally, we made sure that the peak of the action potential corresponds to $\pi$ (see Figure LINK),
so that it becomes straightforward to compare the phase field with the action potential.

Next, we will create a triangulated mesh and compute the phase index for each triangle at each time step.
In theory, the cells of the mesh could be any polygon,
but triangulated meshes are quite common and choosing so, made the code simpler.

<!-- Find references for this method or a formal definition of phase jumps -->

For any polygon, the phase index can be calculated by counting the number of phase jumps.
An algorithm for this will look like:

1. Compute the phase difference $\Delta\Phi$ of all edges.
2. Count the number of times $\Delta\Phi$ is bigger than $\pi$ (positive phase jump).
3. Count the number of times $\Delta\Phi$ is smaller than $-\pi$ (negative phase jump).
4. Calculate the index with $I = P - N$ with $P$ and $N$ the number of positive and negative phase jumps respectively.

## Extended Phasemapping

To extend the naive approach, the first thing to do is localizing the phase defects.
Remember that phase defects are defined as discontinuities in the phase field.
In a triangulated mesh this would manifest as a big phase difference on the edges.
Therefore, the most straightforward thing to do is setting a threshold $d$ so that an edge with a phase difference $\Delta\Phi$
that satisfies $d<\Delta\Phi<2\pi-d$ would be considered as a phase defect.
We have found that a value of $d=0.08\pi$ works best for this simulation,
but keep in mind that this threshold depends highly on the parameters of the simulation.

Once all phase defects are located,
the cells that contain at least one phase defect are removed.
This will create holes in the mesh, allowing us to treat phase defect and boundaries as the same.

Finally, the boundaries and holes are extracted as polygons.
The naive phasemapping approach (see previous section) is then applied to these polygons together with the remaining cells.

# Results

Looking back at Figure~LINK, it is clear that the naive and extended approach does not give the result.
Notice that the naive approach localizes rotational activity in the bottom right and left
while the extended approach localizes rotational activity in the bottom right and around the non-conductive region at the top.
Moreover, the analysis of the naive approach does not satisfy the index theorem given in equation LINK.
This should raise some suspicion that this analysis inaccurate.

<!-- We also highly recommend the reader to watch the video of the simulation. -->
<!-- we would also like to mention that the boundary is accounted for in the extended approach. -->
<!-- It just happens to be that there is no rotation at the outer boundary. -->

![Zoom of the bottom left of the simulation, showcasing a counterclockwise rotation.
Left: A snapshot at time step 172,
with the colours represent the phase of the points at that time step.
Rotors and critical cycles are annotated in red.
Right: The phase density map taken across the entire time of the simulation.
The colours represent the number of time steps that a point was annotated.
A log scale was used to enhance visibility.
The results of the naive approach are displayed at the top,
and the results of the extended approach the bottom.](paper/figures/zoom_rotor.png)

<!-- Maybe, go into more detail about the movement of the rotor and phase defect. -->

First, let's focus on the bottom left (see Figure~LINK).
Both approaches identify rotational activity in this region,
and by comparing both point density maps,
it is clear that they also recognize a similar drift.
However, the extended approach detects a phase defect at the centre of the rotational activity,
indicating that this is a linear rotor,
while this information is not present in the analysis of the naive approach.

![Zoom of the bottom right of the simulation,
showcasing a phase defect without rotation.
From left to right, snapshots are taken at time steps 157, 177 and 235.
The colours represent the phase of the points at that time step.
(Counter)clockwise rotation is annotated in red (blue)
and phase defect without rotation is annotated in white.
The results of the naive approach are displayed at the top,
and the results of the extended approach the bottom.](paper/figures/zoom_defect.png)

Next, we shift focus to the bottom right (see Figure~LINK).
Looking at the snapshots of the simulation,
the naive approach highlight two rotors in opposite direction, which collide with each other before making a complete turn.
In contrast, the extended approach does not identify rotors in this region.
Instead, it finds a phase defect that is located between the two rotors.
What happened here is that the extended approach calculated the phase index of both rotors together,
and since these are of opposite sign,
they cancel each other out.

![Zoom of the top of the simulation,
showcasing rotation around a non-conductive region.
Only the results of the extended approach are shown,
since the naive approach did not detect anything.
From left to right and top to bottom,
snapshots are taken at time steps 132, 172 and 198.
The colours represent the phase of the points at that time step and
critical cycles with clockwise rotation are annotated in blue.](paper/figures/zoom_reentry.png)

Finally, we look at the top of the simulation (see Figure~LINK).
We now have the opposite situation as before at the bottom right:
The extended approach finds rotational activity around the non-conductive tissue while the naive approach does not.
A closer observation of the different snapshots reveals an interesting pattern:
The number of wavefronts around the non-conductive tissue alternates between one and three.
But what makes is even more peculiar is that none of the wavefronts makes a complete turn.
This reminds us about the pattern seen in the bottom right where two rotors collide with each other before completing a turn.
Yet, this time the total phase index is non-zero.

<!-- rewrite all of this -->

# Discussion

The presented simulation is nothing out of the ordinary.
It has only three main components:
a linear core, rotation around a non-conductive region and a phase defect.
That is it. No anisotropic conductivity, no fibres and no noise.
The simulation is also of a good resolution, which also favours phasemapping.
Yet, it can cause trouble for phasemapping if not treated properly.

<!-- Check out revertebators -->

As expected, phasemapping is good at finding rotors,
which is why both approaches find rotational activity at the bottom left.
Nevertheless, the rotor in this simulation has a linear core
and, as discussed in [@arno2021a, @tomii2021spatial], is different from a rotor tip.

<!-- Not sure about this -->

Discussing the phase defect instead of the rotor tip would also simplify the description of the rotor movement.
Notice that the rotor tip is always attached to the phase defect.
This means that you can split up the movement of the rotor tip as a rotation around the phase defect
and the movement of the phase defect.
What we are implying is that just the movement of the phase defect is enough to describe the dynamics of the system
and that is generally less complex.

In contrast to the successful detection of rotors,
we have demonstrated that phase defects can cause false positives, as seen in Figure~LINK.
Some people would dismiss these rotors tips by stating that they do not make a full rotation,
but this would require a visual inspection or post-processing steps.
Accounting for phase defects dismisses these rotors already,
reducing the necessary steps to get to the correct interpretation.

However, phase defects do not tell the whole story.
For example, looking at the phase defect,
the discontinuity disappears when the wavefront is moving away from it,
but the next wave still can't pass through it.

Since the phase space of cardiac tissue can exhibit interfaces or defects,
it is not necessarily guaranteed that phasemapping and waveback -and front intersection points give the correct analysis.
This could explain the reason why using different thresholds to count phase jumps,
gives different results. (LINK!!!)

Not much attention is given to non-conductive structures, but they do play an import role in the clinical field.
As for the pattern in the presented simulation, it turns out that this used to be dismissed as not important.
However, recent studies have found that these play a critical role in the success of ablation therapies [@duytschaever2024atrial, @santucci2024identification, @takigawa2019a].

Our naive implementation did not detect anything around the non-conductive tissue,
but in case an implementation searches for rotors by looking at the endpoints of the wavefront,
it would detect either one or three rotors.
While a phase density map would then highlight the full boundary,
the interpretation would be a bit messy.
Especially if you consider rotors only to be true if they make a full rotation.
Calculating the phase index of the boundary gives a clearer interpretation
and is therefore preferred.

One could argue that the naive approach that was used,
was too simplistic and that current algorithms would do a better job at analysing this simulation.
However, we have not encountered implementation of rotor detection that explicitly account for this.

## Future work

- Fibrotic tissue are trouble since they make the field not smooth
- Test out noisy data, could phase defect make phasemapping more robust @tomii2021spatial
  Finite wavelength could give an additional requirement which can limit false positives
- Paper kabus2024 --> phase definitions, sawtooth
- Limitations: identifying phase defects

# Conclusion

- Properly addressing phase defects and adapting the curve can make phasemapping
  suitable for analysing clinical cases.
- Refer to preregistration.
- Additionally, we encourage research groups to try out this simple example
  to see whether their detection method can analyse this map correctly.
  However, keep in mind Goodhart's Law

This paper is meant to serve as a theoretical backbone to understand
how phasemapping can be used in a clinical setting.
Researcher who are interested in testing these ideas,
can have a look at our preregistration (LINK!!!).

# Data availability

- GitHub: code + source code
- Zenodo: figures, simulation data, video
- OSF: preregistration

Readers who would like to reproduce our results are referred to this GitHub repository (LINK!!!),
which contains the used code and some further explanation.
