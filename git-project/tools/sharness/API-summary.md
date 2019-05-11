# API Summary

## CONSTANTS:

SHARNESS_VERSION
SHARNESS_TEST_EXTENSION
SHARNESS_ORIG_TERM
SHARNESS_TEST_DIRECTORY
SHARNESS_TEST_SRCDIR
SHARNESS_BUILD_DIRECTORY
SHARNESS_TEST_FILE
SHARNESS_TRASH_DIRECTORY

## FRAMEWORK FUNCTIONS
test_set_prereq()
test_have_prereq()

### Hooks
test_when_finished()
cleanup

### Debug
test_debug()
test_pause()

## TESTCASE FUNCTIONS
test_expect_success()
test_expect_failure()
test_done()

## INSIDE TESTCASE FUNCTIONS
test_must_fail()
test_might_fail()
test_expect_code()

### Comparison Functions
test_cmp()
test_seq()
test_must_be_empty()
test_equal()
