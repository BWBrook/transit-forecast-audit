#!/usr/bin/env Rscript

# Independent Track-R reproduction from the raw OSF text files.
# This script intentionally uses only base R and does not import package
# readers or the Python reproduction.
options(stringsAsFactors = FALSE, scipen = 999)
root <- normalizePath(getwd())
out_dir <- file.path(root, "results", "pilot_v1", "independent_review")
full_dir <- file.path(root, "data", "derived", "independent_table5")
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)
dir.create(full_dir, recursive = TRUE, showWarnings = FALSE)

parse_tab <- function(path, expected) {
  lines <- readLines(path, warn = FALSE, encoding = "UTF-8")
  keep <- nzchar(trimws(lines)) & !grepl("^\\s*#", lines)
  raw <- lines[keep]
  # Catalogue headers are plain text; omit them. The outcome file stores the
  # planet and first numeric field in one space-padded field, unlike DRB.
  is_header <- grepl("^\\s*(Planet|Tmid)\\b", raw)
  raw <- raw[!is_header]
  fields <- strsplit(raw, "\\t")
  fields <- lapply(fields, function(x) {
    if (length(x) == expected - 1L) {
      first <- strsplit(trimws(x[1]), "[[:space:]]+")[[1]]
      c(first, x[-1])
    } else x
  })
  if (any(lengths(fields) < expected)) stop(sprintf("short non-comment line in %s", path))
  out <- as.data.frame(do.call(rbind, lapply(fields, function(x) x[seq_len(expected)])),
                       stringsAsFactors = FALSE)
  out$raw_line <- raw
  out$raw_line_no <- which(keep)[!is_header]
  out
}

read_ephem <- function(path, release) {
  if (release == "DRB") {
    x <- parse_tab(path, 17L)
    names(x)[1:17] <- c("planet", "t0", "t0_unc", "period", "period_unc", "scale",
                        "mean", "median", "sd", "rms", "chi", "redchi", "autocorr",
                        "shapiro", "nonlinear", "highfreq", "link")
    x$nonlinear <- tolower(x$nonlinear) %in% c("true", "1", "yes")
  } else {
    x <- parse_tab(path, 5L)
    names(x)[1:5] <- c("planet", "t0", "t0_unc", "period", "period_unc")
    x$nonlinear <- FALSE
  }
  for (nm in names(x)[seq_len(min(17L, ncol(x)))]) x[[nm]] <- trimws(x[[nm]])
  for (nm in c("t0", "t0_unc", "period", "period_unc")) x[[nm]] <- as.numeric(x[[nm]])
  x$release <- release
  x
}

read_outcomes <- function(path) {
  x <- parse_tab(path, 5L)
  names(x)[1:5] <- c("planet", "tmid", "tmid_unc", "source", "id")
  for (nm in names(x)[1:5]) x[[nm]] <- trimws(x[[nm]])
  x$tmid <- as.numeric(x$tmid); x$tmid_unc <- as.numeric(x$tmid_unc)
  x
}

manifest_path <- file.path(root, "results", "pilot_v1", "source_manifest.csv")
manifest <- read.csv(manifest_path, stringsAsFactors = FALSE, check.names = FALSE)
manifest$exists <- file.exists(file.path(root, manifest$local_path))
manifest$sha256_observed <- NA_character_
for (i in seq_len(nrow(manifest))) {
  p <- file.path(root, manifest$local_path[i])
  if (manifest$exists[i]) {
    got <- system2("shasum", c("-a", "256", shQuote(p)), stdout = TRUE, stderr = FALSE)
    manifest$sha256_observed[i] <- strsplit(got, "[[:space:]]+")[[1]][1]
  }
}
manifest$hash_match <- manifest$exists & !is.na(manifest$sha256_observed) &
  manifest$sha256_observed == manifest$sha256
write.csv(manifest[, c("source_id", "release", "local_path", "sha256", "sha256_observed",
                       "exists", "hash_match")],
          file.path(out_dir, "table5_manifest_check.csv"), row.names = FALSE, quote = TRUE)
if (!all(manifest$hash_match)) stop("source manifest hash verification failed")

ephem <- list(
  DRB = read_ephem(file.path(root, "data/raw/osf/wna5e/updated_ephemerides.txt"), "DRB"),
  DRC = read_ephem(file.path(root, "data/raw/osf/p298n/catalogue_of_ephemerides.txt"), "DRC"),
  DRD = read_ephem(file.path(root, "data/raw/osf/wpjtn/catalogue_of_ephemerides.txt"), "DRD")
)
for (rel in names(ephem)) {
  x <- ephem[[rel]]
  if (anyDuplicated(x$planet)) stop(sprintf("duplicate forecast planet in %s", rel))
  if (any(!is.finite(x$t0) | !is.finite(x$t0_unc) | !is.finite(x$period) |
          !is.finite(x$period_unc) | x$t0_unc <= 0 | x$period <= 0 | x$period_unc <= 0))
    stop(sprintf("invalid forecast numeric value in %s", rel))
}
out <- read_outcomes(file.path(root, "data/raw/osf/wpjtn/all_mid_time_data.txt"))
if (any(!is.finite(out$tmid) | !is.finite(out$tmid_unc) | out$tmid_unc <= 0))
  stop("invalid outcome timing or uncertainty")
if (anyDuplicated(out$id[out$source == "space" & grepl("_TESS$", out$id)]))
  stop("duplicate TESS outcome record ID")
out$id_date_parse_ok <- grepl("_[0-9]{4}-[0-9]{2}-[0-9]{2}_TESS", out$id)
out$date <- as.Date(NA_character_)
out$date[out$id_date_parse_ok] <- as.Date(sub(".*_([0-9]{4}-[0-9]{2}-[0-9]{2})_TESS.*", "\\1", out$id[out$id_date_parse_ok]))
dev_end <- as.Date("2024-01-03")
if (any(out$id_date_parse_ok & !is.na(out$date) & out$date > dev_end))
  stop("outcome date exceeds development-era upper bound")

# Transcribed from the versioned ExoClock II/III/IV article source records and used
# only to reproduce the published screening rule.
drd_ttv <- c("HD106315c", "HD108236b", "HD191939c", "HD191939d", "HD28109c", "K2-19b",
             "K2-19c", "K2-21c", "KOI-12b", "KOI-94c", "Kepler-18d", "Kepler-396c",
             "L98-59b", "L98-59c", "TOI-1130b", "TOI-1130c", "TOI-1136c", "TOI-1136d",
             "TOI-1136e", "TOI-1136f", "TOI-1246d", "TOI-125b", "TOI-2076b", "TOI-2076c",
             "TOI-216.01", "TOI-216.02", "TOI-270c", "TOI-270d", "TOI-712c", "WASP-148b",
             "HAT-P-7b", "HD332231b", "KELT-9b", "TOI-201b", "TOI-1333b", "TrES-3b",
             "WASP-4b", "WASP-12b", "WASP-19b", "WASP-33b", "WASP-135b", "WASP-161b")

score_release <- function(rel, exclusion) {
  f <- ephem[[rel]]
  elig <- out$source == "space" & grepl("_TESS$", out$id) & out$id_date_parse_ok &
    !is.na(out$date) & out$date >= as.Date("2022-01-01") & out$date <= dev_end
  if (anyDuplicated(paste(out$planet[elig], out$id[elig], sep = "|")))
    stop(sprintf("duplicate scored outcome planet/record ID in %s", rel))
  o <- out[elig, c("planet", "tmid", "tmid_unc", "source", "id", "date", "raw_line_no")]
  names(o)[names(o) == "raw_line_no"] <- "outcome_raw_line_no"
  m <- merge(o, f[, c("planet", "t0", "t0_unc", "period", "period_unc", "nonlinear",
                      "raw_line_no")], by = "planet", all = FALSE, sort = FALSE)
  names(m)[names(m) == "raw_line_no"] <- "forecast_raw_line_no"
  m$excluded_flag <- m$planet %in% exclusion
  m <- m[!m$excluded_flag, , drop = FALSE]
  m$epoch <- round((m$tmid - m$t0) / m$period)
  m$predicted <- m$t0 + m$epoch * m$period
  m$residual <- m$tmid - m$predicted
  m$sigma_oc <- sqrt(m$tmid_unc^2 + m$t0_unc^2 + (m$epoch * m$period_unc)^2)
  m$z_abs <- abs(m$residual) / m$sigma_oc
  write.csv(m, file.path(full_dir, paste0("table5_events_", tolower(rel), ".csv")),
            row.names = FALSE, quote = TRUE)
  data.frame(release = rel, forecast_planets = length(unique(f$planet)),
             excluded_planets = sum(unique(f$planet) %in% exclusion),
             planets_scored = length(unique(m$planet)), measurements = nrow(m),
             n_lt_1 = sum(m$z_abs < 1), n_lt_2 = sum(m$z_abs < 2),
             n_lt_3 = sum(m$z_abs < 3), n_lt_4 = sum(m$z_abs < 4),
             p_lt_1 = 100 * mean(m$z_abs < 1), p_lt_2 = 100 * mean(m$z_abs < 2),
             p_lt_3 = 100 * mean(m$z_abs < 3), p_lt_4 = 100 * mean(m$z_abs < 4),
             stringsAsFactors = FALSE)
}

# The numerically matching Table 5 reconstruction applies the DRD TTV exclusion.
# The origin-only variants are a separate sensitivity and are not this R match.
res <- rbind(score_release("DRB", drd_ttv), score_release("DRC", drd_ttv),
             score_release("DRD", drd_ttv))
write.csv(res, file.path(out_dir, "table5_independent_summary.csv"), row.names = FALSE, quote = TRUE)
# Compact, tracked-friendly trace sample: same raw line identities as the full
# event files, restricted to the ten pilot queue planets.
trace_planets <- c("HAT-P-12b", "HAT-P-27b", "HD209458b", "Qatar-1b", "WASP-12b",
                   "WASP-43b", "WASP-52b", "WASP-69b", "WASP-74b", "WASP-80b")
trace <- do.call(rbind, lapply(c("DRB", "DRC", "DRD"), function(rel) {
  z <- read.csv(file.path(full_dir, paste0("table5_events_", tolower(rel), ".csv")),
                stringsAsFactors = FALSE)
  z$release <- rel
  z[z$planet %in% trace_planets, c("release", "planet", "id", "outcome_raw_line_no",
                                  "forecast_raw_line_no", "date", "epoch", "residual",
                                  "sigma_oc", "z_abs")]
}))
write.csv(trace, file.path(out_dir, "table5_event_trace_subset.csv"), row.names = FALSE, quote = TRUE)
script_hash <- system2("shasum", c("-a", "256", shQuote(file.path(root, "scripts", "independent_table5.R"))), stdout = TRUE)
source_commit <- system2("git", c("rev-parse", "HEAD"), stdout = TRUE)
runtime <- c(
  paste0("command: Rscript scripts/independent_table5.R"),
  paste0("script_sha256: ", strsplit(script_hash, "[[:space:]]+")[[1]][1]),
  paste0("source_commit: ", source_commit),
  "independent_source: 42 DRD TTV names independently transcribed from arXiv:2511.14407v1 main.tex (text plus TTV table), not a repository fixture; source URL https://arxiv.org/src/2511.14407v1 .",
  capture.output(sessionInfo()), "", capture.output(str(res)))
writeLines(sub("[[:space:]]+$", "", runtime), file.path(out_dir, "table5_runtime.txt"))
cat(paste(capture.output(print(res)), collapse = "\n"), "\n")
