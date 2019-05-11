package com.zenterio.jenkins.configuration

/**
 * The Priority enum is used to configure priority of an Origin.
 * Priority is absolute, where High-priority jobs always skip ahead of lower-prio
 * jobs in the queue.
 */
public enum Priority {
    HIGH(1),
    MEDIUM(2),
    LOW(3),

    /**
     * Priority value as an int.
     */
    final int value

    /**
     * @param value As an int
     */
    private Priority(int value) {
        this.value = value
    }

    public static Priority getFromString(String priorityName) {
        return priorityName?.toUpperCase() as Priority
    }

}
