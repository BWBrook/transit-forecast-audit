# Focused astronomical background

This primer identifies concepts to learn while doing the pilot. It supplements
the cited astronomical papers; it does not establish any new empirical claim.

## What is measured and what is predicted?

A light curve is a sequence of measured brightness values. During a transit,
the planet obscures a portion of its host star. A transit model and a model for
the surrounding baseline yield an estimate of the midpoint, along with its
uncertainty. A timing catalogue contains those estimates, not exact physical
times. The estimate can depend on data gaps, detrending, limb-darkening
assumptions, stellar variability and the timing prior used in the fit.

An ephemeris maps an integer transit number to a predicted midpoint. A linear
ephemeris assumes a constant interval between successive transits over the
relevant span. The epoch zero is a coordinate choice, so different published
ephemerides can use different zero points for the same physical transit series.

## The baseline and its departures

The baseline parameters are a reference midpoint and the orbital period. Their
joint uncertainty determines how prediction uncertainty grows away from the
region constrained by the observations. A period estimated from a short span
can have a small quoted uncertainty and still be a poor long-range model if
unmodelled behaviour exists.

Transit-timing variations (TTVs) describe departures from an adopted timing
model. They can arise from dynamical interactions and other physical effects,
but a large timing residual is not, by itself, evidence for a new planet or
orbital decay. Timing conventions, measurement systematics and an inaccurate
ephemeris also require investigation. Read
[Agol & Fabrycky's updated review](https://arxiv.org/abs/1706.09849v4) and the physical
discussion in [ExoClock IV](https://doi.org/10.3847/1538-4365/ae3238).

For the first study, known nonlinear systems are useful challenge cases and
historical strata. Building new dynamical models for them would substantially
expand the scope. A failure of a linear prediction can remain part of an honest
historical forecast evaluation even if its physical explanation is learned later.

## Time conventions

Julian dates count days, but the number alone does not identify the clock or
reference location. Heliocentric and barycentric corrections differ; UTC and TDB
differ. A shortened numerical offset, such as the convention used in a mission's
time column, is another independent part of the metadata.

The working normalisation is BJD_TDB. It must be established from the source or
converted with the appropriate information and tested software. The numerical
code accepts only explicitly normalised inputs and does not perform that
conversion. [Eastman, Siverd & Gaudi 2010](https://doi.org/10.1086/655938) is the
essential first reading on this topic.

## Covariance and the reference epoch

Period and reference time often covary in a fit. Omitting this term can change a
future uncertainty substantially. Placing the reference epoch near the weighted
centre of the fitted observations can reduce that covariance in a simple linear
model. Transforming the covariance to a different pivot must leave the physical
prediction unchanged. Read [Deeg 2015](https://doi.org/10.1051/0004-6361/201425368).

Three ages should never be confused: time since public issuance, time since the
last input observation, and numerical distance from the parameter pivot. They
have different interpretations even when a catalogue calls all of them epochs.

## Why TESS is attractive, and why it is not a complete census

The candidate route uses public TESS observations because extended space-based
light curves can supply baseline around a transit and record many successive
events. Nonetheless, target coverage, data gaps, detection thresholds and the
availability of reliable individual midpoints matter. A planet with no suitable
future TESS timing has no measured forecast error in this design. It is not a
forecast success.

The MAST data portal and its release/version fields are described in
`data_sources.md`. Keep acquisition time, public data release and pipeline
processing version distinct. A modern reduction of an old exposure is the same
underlying observation for independence purposes.

## How timing accuracy becomes operational value

To capture a full transit, an observing window must cover its ingress, egress
and any required baseline, not simply its midpoint. Transit duration has its own
uncertainty, and a ground observatory has visibility and weather constraints.
Thus midpoint forecast coverage is one component of observing success.

For the first paper, a well-defined timing-margin calculation is an appropriate
ancillary analysis. A claim to optimise telescope allocation requires an explicit
decision model and opportunities/attempts beyond the successful timings.

## Suggested learning order

1. Read one planet's source ephemeris and light-curve timing record end to end.
2. Recompute a forecast and its full variance manually and in code.
3. Resolve the source's time standard and epoch numbering.
4. Trace one TESS event to its original samples and reduction.
5. Read the closest population-evaluation studies.
6. Only then add physical model complexity that the selected question requires.
