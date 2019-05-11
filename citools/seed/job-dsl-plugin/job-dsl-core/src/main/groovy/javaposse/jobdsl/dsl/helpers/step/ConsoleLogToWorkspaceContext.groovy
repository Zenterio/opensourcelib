package javaposse.jobdsl.dsl.helpers.step

import javaposse.jobdsl.dsl.Context

class ConsoleLogToWorkspaceContext implements Context {

    boolean writeConsoleLog = true
    boolean blockOnAllOutput = true

    /**
     * If set to false, the console log will not be written to workspace file.
     * @param writeConsoleLog
     */
    void writeConsoleLog(boolean writeConsoleLog = true) {
        this.writeConsoleLog = writeConsoleLog
    }

    /**
     * If set to false, the plugin will not wait for more output.
     * @param writeConsoleLog
     */
    void blockOnAllOutput(boolean blockOnAllOutput = true) {
        this.blockOnAllOutput = blockOnAllOutput
    }

}
