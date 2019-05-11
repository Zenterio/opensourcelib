package com.zenterio.jenkins.configuration

/**
 * The CcacheSize enum is used to designate the size of
 * the CCache, as described by the CCache documentation
 * for max size.
 *
 **/
public enum CcacheSize {
    SMALL('3G'),
    MEDIUM('4G'),
    LARGE('5G'),
    OVER_SIZE('6G'), /** not used in configuration, used for non-publishing */

    /**
     * Size value as a string including unit, e.g. "4G"
     */
    final String value

    /**
     * @param value As a string including unit.
     */
    private CcacheSize(String value) {
        this.value = value
    }

    public static CcacheSize getFromString(String sizeName) {
        return sizeName?.toUpperCase() as CcacheSize
    }
}
