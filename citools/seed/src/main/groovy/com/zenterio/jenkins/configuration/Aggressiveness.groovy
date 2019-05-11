package com.zenterio.jenkins.configuration

public enum Aggressiveness {
    LOW('low'),
    MEDIUM('medium'),
    HIGH('high'),

    public final String level

    private Aggressiveness(String level) {
        this.level = level
    }

    @Override
    public String toString() {
        return this.level
    }
}
