# Reproduce the main table for this experiment: N=30, ITER=20.
# Usage: awk -f analyze_results.awk results.csv > recalculated.csv
BEGIN { FS = ","; OFS = ","; critical = 2.045229642132703 }
NR == 1 { next }
{
    if (NF != 19 || $7 != 20 || $17 != 0 || $19 != 436905) {
        print "ERROR: Unexpected data at line " NR > "/dev/stderr"
        failed = 1
        exit 1
    }
    key = $4 "_" $5
    if (!(key in n)) order[++groups] = key
    value = $10 * 1000 / $7
    n[key]++
    delta = value - mean[key]
    mean[key] += delta / n[key]
    m2[key] += delta * (value - mean[key])
}
END {
    if (failed) exit 1
    if (groups != 4) exit 1
    for (i = 1; i <= groups; i++) {
        key = order[i]
        if (n[key] != 30) {
            print "ERROR: This script uses the t quantile for N=30" > "/dev/stderr"
            exit 1
        }
    }
    print "group,n,mean_ms_per_pass,sd_ms_per_pass,ci95_low,ci95_high,relative_half_pct"
    for (i = 1; i <= groups; i++) {
        key = order[i]
        sd = sqrt(m2[key] / (n[key] - 1))
        half = critical * sd / sqrt(n[key])
        printf "%s,%d,%.9f,%.9f,%.9f,%.9f,%.9f\n", key, n[key], mean[key], sd, mean[key]-half, mean[key]+half, 100*half/mean[key]
    }
}
