package com.zenterio.jenkins.configuration

class ConfigError extends Exception
{
    public ConfigError(String message="") {
        super(message)
    }
}

