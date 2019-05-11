from zaf.config import ConfigException


def parse_time(timestring):
    """Parse time strings in the [[hh:]mm:]ss format into seconds."""

    invalid_time_error = "Invalid time specified: '{time}'. Format is '[[hh:]mm:]ss'".format(
        time=timestring)
    if not timestring:
        return None

    times = timestring.split(':')
    seconds = 0
    exponent = 0
    if len(times) > 3:
        raise ConfigException(invalid_time_error)
    try:
        for timepart in reversed(times):
            seconds += int(timepart) * (60**exponent)
            exponent += 1
    except ValueError:
        raise ConfigException(invalid_time_error)
    return seconds
