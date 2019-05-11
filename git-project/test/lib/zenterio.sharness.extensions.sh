
# If the argument is a file, that file is copied to a placeholder file expected.
# Otherwise, the content of what is passed, is written to the file expected.
set_expected() {
    if [ -f "$@" ]; then
        cat "$@" > "${SHARNESS_TRASH_DIRECTORY}/expected"
    else
        echo -e "$@" > "${SHARNESS_TRASH_DIRECTORY}/expected"
    fi
}

# If the argument is a file, that file is copied to a placeholder file actual.
# Otherwise, the content of what is passed, is written to the file actual.
set_actual() {
    if [ -f "$@" ]; then
        cat "$@" > "${SHARNESS_TRASH_DIRECTORY}/actual"
    else
        echo -e "$@" > "${SHARNESS_TRASH_DIRECTORY}/actual"
    fi
}

# $1 - actual
# $2 - expected
test_equal() {
    local actual="$1"
    shift
    local expected="$1"
    shift
    local extra=$@
    if [ -z "extra" ]; then
        error "Extra arguments to expect_equal"
        return 128
    fi
    set_expected "${expected}"
    set_actual "${actual}"
    test_cmp "${SHARNESS_TRASH_DIRECTORY}/actual" "${SHARNESS_TRASH_DIRECTORY}/expected"
}

# do nothing, disable test
xtest_expect_success() {
    :
}

# do nothing, disable test
xtest_expect_failure() {
    :
}

# Execute command in sub-shell and redirect output to match sharness schema.
test_exec() {
        ("$@") <&6 >&3 2>&4
}
