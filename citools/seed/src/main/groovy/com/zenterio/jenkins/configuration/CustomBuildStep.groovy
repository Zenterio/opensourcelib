package com.zenterio.jenkins.configuration


import groovy.transform.AutoClone
import groovy.transform.AutoCloneStyle
import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode

/**
 * The custom build step represents a build-step in a jenkins job.
 * <p>
 * Custom build steps are inherited only if an item has no custom
 * build step of its own.
 * <p>
 * It can replace the default build steps for the builds, or add
 * additional build steps depending on the positional mode:
 * <dl>
 * <dt>prepend<dt><dd>This adds a build step before the other build step modes.</dd>
 * <dt>override<dt><dd>This overrides the default build steps.</dd>
 * <dt>append<dt><dd>This will append the build step after the other build step modes.</dd>
 * <dt>override-named<dt><dd>This will override a single named build step and keep all the others.</dd>
 * </dl>
 * If there is no "mode=override" custom build step, the standard builds steps
 * will be created.
 * <p>
 * If mode is left out, the mode will be override.
 * <p>
 * Within each mode, the builds steps will be added in the order they are declared except for override-named
 * that will keep the order of the original build steps.
 * <p>
 * overrideName is used together with override-named to specify the name of the build step to override.
 */
@Canonical
@EqualsAndHashCode(callSuper=true, includeFields=true)
@AutoClone
class CustomBuildStep extends BaseConfig {

    final static CustomBuildStepType DEFAULT_TYPE = CustomBuildStepType.SHELL

    /**
     * The code in the custom build step
     */
    String code

    /**
     * Positioning mode
     */
    CustomBuildStepMode mode

    /**
     * Enabled
     */
    Boolean enabled

    /**
     * The type of buildstep, i.e the language used in it
     */
    CustomBuildStepType type

    /**
     * If mode is OVERRIDE_NAME this is used to specify the name of the build step to override
     */
    String overrideName

    /**
     * Custom build step for projects, origins and products.
     *
     * @param code Shell code build step
     * @param mode Custom build step positioning mode
     * @param enabled If the build step should be generated or not
     */
    public CustomBuildStep(String code, CustomBuildStepMode mode, Boolean enabled, CustomBuildStepType type=DEFAULT_TYPE, String overrideName=null) {
        this.code = code
        if (mode == null) {
            this.mode = CustomBuildStepMode.OVERRIDE
        } else {
            this.mode = mode
        }
        this.enabled = enabled ?: false
        this.type = type ?: DEFAULT_TYPE
        this.overrideName = overrideName
    }

    public static CustomBuildStep getTestData() {
        return new CustomBuildStep("CODE", CustomBuildStepMode.APPEND, true, DEFAULT_TYPE)
    }
}
