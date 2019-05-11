
/**
 * Default use
 */
job('example-1') {
    steps {
        consoleLogToWorkspace('console.log')
    }
}

/**
 * Disable blocking (waiting) for delayed output
 * Disable writing to file entirely
 */
job('example-2') {
    steps {
        consoleLogToWorkspace('console.log') {
            blockOnAllOutput(false)
            writeConsoleLog(false)
        }
    }
}
