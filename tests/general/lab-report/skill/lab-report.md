# Measuring g with a simple pendulum

PHYS 101, October 9, 2026. Author: [needs: author name]. Partner: Dev. Instructor: Dr. Alvarez.

## Purpose

We measured the acceleration due to gravity, g, from the period of a simple pendulum and compared it with the accepted value of 9.81 m/s^2. Our result is 9.78 m/s^2 (mean of five lengths), 0.3% below the accepted value.

## Method

We hung a metal bob on a string from a clamp on a stand. We measured the length L from the pivot to the center of the bob with a meter stick, good to about ±0.5 cm. We released the bob from about 10 degrees each time, which keeps the small-angle formula valid.

For each trial we timed 10 full oscillations with a phone stopwatch. We ran 3 trials at each of 5 lengths. At 0.20 m the bob hit the stand once, so we redid that trial.

## Data

Times are for 10 oscillations. The period is T = (mean time) / 10.

| L (m) | Trial 1 (s) | Trial 2 (s) | Trial 3 (s) | Mean time (s) | T (s) |
|---|---|---|---|---|---|
| 0.20 | 9.1 | 8.9 | 9.0 | 9.0 | 0.900 |
| 0.40 | 12.7 | 12.6 | 12.8 | 12.7 | 1.270 |
| 0.60 | 15.6 | 15.4 | 15.5 | 15.5 | 1.550 |
| 0.80 | 18.0 | 17.9 | 18.1 | 18.0 | 1.800 |
| 1.00 | 20.2 | 20.0 | 20.1 | 20.1 | 2.010 |

## Analysis

The handout gives T = 2π√(L/g), so g = 4π²L / T². We computed g for each length from the mean period. Example for L = 1.00 m: g = 4π² × 1.00 / (2.01)² = 9.77 m/s^2. The values below are computed from the table.

| L (m) | T (s) | g (m/s^2) |
|---|---|---|
| 0.20 | 0.900 | 9.75 |
| 0.40 | 1.270 | 9.79 |
| 0.60 | 1.550 | 9.86 |
| 0.80 | 1.800 | 9.75 |
| 1.00 | 2.010 | 9.77 |

The mean of the five values is 9.78 m/s^2, with a standard deviation of 0.05 m/s^2. The difference from 9.81 is (9.78 − 9.81) / 9.81 = −0.3%.

As a second check, the formula gives T² = (4π²/g) L, so a plot of T² against L is a line with slope 4π²/g. A least-squares fit of our five points gives a slope of 4.04 s²/m and an intercept of −0.005 s². Then g = 4π² / 4.04 = 9.76 m/s^2, which is 0.5% below 9.81. The intercept is near zero, as the formula predicts.

## Results

| Method | g (m/s^2) | Difference from 9.81 |
|---|---|---|
| Mean of five lengths | 9.78 | −0.3% |
| Slope of T² vs L | 9.76 | −0.5% |

Both results are slightly below the accepted value. The spread between lengths (9.75 to 9.86) is small.

## Sources of error

- Reaction time. Starting and stopping a phone stopwatch by hand may add about 0.2 s to each timing. Because we timed 10 oscillations, the error in one period is about 0.02 s. If that error were all in one direction, g would shift by about 2% at L = 1.00 m (20.1 s) and about 4% at L = 0.20 m (9.0 s). Longer lengths are less affected, since the same 0.2 s is a smaller share of a longer time.
- Length. A ±0.5 cm reading is 2.5% of 0.20 m and 0.5% of 1.00 m. This also weighs most on the short lengths.
- Bob hitting the stand. We redid the affected 0.20 m trial.
- String stretch. We suspected the string stretched slightly. We did not measure it, so we do not know its effect.
- Release angle. We released from about 10 degrees, an approximate angle.

Trial times at each length differ by at most 0.2 s, about the size of the reaction-time estimate.

## Conclusion

Our two methods gave g = 9.78 and 9.76 m/s^2, within 0.5% of 9.81 m/s^2. The difference is smaller than the 2% to 4% timing error that reaction time could cause, so we cannot say the gap is real. To improve the result, time more oscillations per trial, use an electronic timer, and take the longest lengths, where timing and length errors are smallest.
