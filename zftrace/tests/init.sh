#!/bin/bash
ME_="${0##*/}"

warn_() { printf >&2 '%s\n' "$*"; }
fail_() { warn_ "$ME_: failed test: $*"; exit 1; }
skip_() { warn_ "$ME_: skipped test: $*"; exit 77; }
framework_failure_() { warn_ "$ME_: framework failure: $*"; exit 99; }
framework_skip_() { warn_ "$ME_: framework skip: $*"; exit 77; }

print_test_name() {
    echo "TC: ${FUNCNAME[1]}"
}

check_prog() {
    "$@" --version > /dev/null 2>&1 ||
        framework_skip_ "$* is not available"
}

strip_report() {
    local report="$1"
    mv "${report}" "${report}.bak"
    cat "${report}.bak" | grep -e "/data/files" > "${report}" ||
        { fail_ "failed to strip report $report."; }
    rm "${report}.bak"
}

ZFTRACE=${*:-../zftrace}
ZFTRACE_LN=${*:-../zftrace-ln}
ZFTRACE_CP=${*:-../zftrace-cp}
ZFTRACE_FILTER=${*:-../zftrace-filter}

test_binary_zftrace_exists() {
    test -f "${ZFTRACE}" || framework_failure "zftrace binary could not be located."
}

test_binary_zftrace_exists

TEST_ROOT_DIR=$(cd "${srcdir=.}" && pwd)
DATA_DIR="${TEST_ROOT_DIR}/data"
SCRIPT_DIR="${TEST_ROOT_DIR}/scripts"

mkdir -p output
echo "" > check.log
