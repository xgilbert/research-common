### Use a sinusoidal approximation to estimate the number of Growing
### Degree-Days above a given threshold, using daily minimum and
### maximum temperatures.
above.threshold <- function(mins, maxs, threshold) {
    ## Determine crossing points
    aboves = mins > threshold
    belows = maxs < threshold
    plus.over.2 = (mins + maxs)/2
    minus.over.2 = (maxs - mins)/2
    two.pi = 2*pi
    d0s = arcsin((threshold - plus.over.2) / minus.over.2) / two.pi
    d1s = .5 - d0s

    d0s[aboves] = 0
    d1s[aboves] = 1
    d0s[belows] = 0
    d1s[belows] = 0

    ## Integral
    F1s = -minus.over.2 * cos(2*pi*d1s) / two.pi + plus.over.2 * d1s
    F0s = -minus.over.2 * cos(2*pi*d0s) / two.pi + plus.over.2 * d0s
    return(sum(F1s - F0s - threshold * (d1s - d0s)))
}

### Get the Growing Degree-Days, as degree-days between gdd.start and
### kdd.start, and Killing Degree-Days, as the degree-days above
### kdd.start.
get.gddkdd <- function(gdd.start, kdd.start) {
    dd.lowup = above.threshold(tasmin, tasmax, gdd.start)
    dd.above = above.threshold(tasmin, tasmax, kdd.start)
    dd.lower = dd.lowup - dd.above

    return(c(dd.lower, dd.above))
}