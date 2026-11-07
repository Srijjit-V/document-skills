# Measuring g with a Simple Pendulum

PHYS 101, performed October 9, 2026. Instructor: Dr. Alvarez. Lab partner: Dev.

## Abstract

We measured the acceleration due to gravity, g, from the period of a simple pendulum at five lengths from 0.20 m to 1.00 m. The mean of the five single-length results is 9.78 m/s^2. A straight-line fit of T^2 against L gives 9.76 m/s^2. Both agree with the accepted value of 9.81 m/s^2 (differences of 0.3% and 0.5%), well inside our estimated uncertainty of about 0.2 m/s^2.

## Objective

Measure g using a simple pendulum and compare it with the accepted value, 9.81 m/s^2.

## Theory

For small oscillation angles the period of a simple pendulum is

T = 2 pi sqrt(L / g),

so

g = 4 pi^2 L / T^2.

Squaring the first form gives T^2 = (4 pi^2 / g) L. A plot of T^2 against L should be a straight line through the origin with slope 4 pi^2 / g.

## Apparatus and Method

- String and metal bob hung from a clamp on a stand.
- Meter stick for length, measured from the pivot to the center of the bob. Readings are good to about +/- 0.5 cm.
- Phone stopwatch.

We used five lengths: 0.20, 0.40, 0.60, 0.80 and 1.00 m. At each length we released the bob from about 10 degrees and timed 10 full oscillations. We did this three times per length. Timing 10 oscillations at once divides the stopwatch error by 10 in the period. The period is the 10-oscillation time divided by 10.

At L = 0.20 m the bob hit the stand during one trial. We discarded that trial and repeated it.

## Data

Times are for 10 full oscillations. T is the mean time divided by 10.

| L (m) | Trial 1 (s) | Trial 2 (s) | Trial 3 (s) | Mean time (s) | T (s) | T^2 (s^2) |
|------:|------------:|------------:|------------:|--------------:|------:|----------:|
| 0.20 | 9.1 | 8.9 | 9.0 | 9.00 | 0.900 | 0.810 |
| 0.40 | 12.7 | 12.6 | 12.8 | 12.70 | 1.270 | 1.613 |
| 0.60 | 15.6 | 15.4 | 15.5 | 15.50 | 1.550 | 2.403 |
| 0.80 | 18.0 | 17.9 | 18.1 | 18.00 | 1.800 | 3.240 |
| 1.00 | 20.2 | 20.0 | 20.1 | 20.10 | 2.010 | 4.040 |

## Analysis

### Method 1: g at each length

Using g = 4 pi^2 L / T^2 with the mean period at each length:

| L (m) | g (m/s^2) |
|------:|----------:|
| 0.20 | 9.75 |
| 0.40 | 9.79 |
| 0.60 | 9.86 |
| 0.80 | 9.75 |
| 1.00 | 9.77 |

The mean is 9.78 m/s^2. The scatter among the five values is small (standard deviation 0.05 m/s^2, standard error 0.02 m/s^2) and shows no trend with length.

### Method 2: slope of T^2 versus L

A least-squares line through the five (L, T^2) points has a slope of 4.04 s^2/m and an intercept of about -0.005 s^2, which is essentially zero, as the theory predicts. The slope gives g = 4 pi^2 / 4.04 = 9.76 m/s^2.

### Uncertainty

The small scatter between lengths understates the real uncertainty, because the main errors are systematic or affect every trial the same way:

- **Timing.** We estimated reaction time at the stopwatch start and stop at up to 0.2 s. On a 10-oscillation time this is 0.02 s in T. That is 2.2% of T at L = 0.20 m and 1.0% at L = 1.00 m. Since g depends on 1/T^2, the effect on g is doubled: about 4% and 2%.
- **Length.** +/- 0.5 cm is 2.5% of 0.20 m but only 0.5% of 1.00 m.
- **Combined at L = 1.00 m**, the best case, the relative uncertainty in g is about 2%, or roughly 0.2 m/s^2. Shorter lengths are less precise, so the longer lengths deserve more weight.

We report **g = 9.78 +/- 0.2 m/s^2**.

## Discussion

Our result is 0.03 m/s^2 (0.3%) below the accepted 9.81 m/s^2, far smaller than our uncertainty, so the experiment is consistent with the accepted value. We cannot claim the agreement is better than the 0.2 m/s^2 uncertainty allows. The slope method gives a similar result, and the near-zero intercept supports the T ∝ sqrt(L) relationship.

Possible systematic effects, none of which we measured:

- **Stretching string.** We were unsure whether the string stretched. If it did, the true length was a little longer than measured, which would make our calculated g slightly low. This matches the direction of our result, but we have no evidence that it explains it.
- **Release angle.** The small-angle formula slightly underestimates the real period at 10 degrees (by roughly 0.2%, from the first correction term, theta^2 / 16). This pushes calculated g low by about 0.4%. Correcting for it would move our result to roughly 9.8 m/s^2. This is a back-of-envelope estimate, since our release angle was only approximate.
- **Reaction time.** Random reaction-time error would add scatter. A consistent delay at start and stop would largely cancel in the elapsed time.
- **Disturbed trial.** The bob hit the stand once at L = 0.20 m. We redid that trial, but the swing may have been slightly disturbed in other trials too.
- **Stopwatch and meter stick resolution.** Both are coarse for the shortest length.

## Conclusion

Using a simple pendulum we measured g = 9.78 +/- 0.2 m/s^2, consistent with the accepted value of 9.81 m/s^2. To improve the measurement we would use a longer pendulum, time more oscillations (20 or more), use a non-stretching string or a thin wire, and time the swing with a photogate or a video frame count rather than by hand.
