/**
 * A scriptlet is a small piece of code that can be injected in a system
 * to define or modify the systems behavior.
 * <p>
 * The scriptlet should be able to access various aspect of the system,
 * such as state as a mean of interaction.
 * <p>
 * The classes included in this package can either be used as base classes
 * to more specialized scriptlet classes that serves as an entry point for
 * interaction to a specific part of the system.
 * However, these specialized classes do not belong in this package; only
 * general purpose classes reside here.
 * <p>
 * Another purpose of the scriptlet could be to act as a data transfer object
 * between two contexts, a delivery mechanism for text data, were a specialized
 * part of the system accept a IScriptlet as input as part of its
 * established interface.
 * <p>
 * The most common way of creating interaction points in a scriptlet is to
 * define macros that expand to system internal data values. A macro expansion
 * engine is built into {@link com.zenterio.jenkins.scriptlet.BaseScriptlet} for
 * that purpose.
 * <p>
 * Specialized scriptlet classes should define the macros made available in its
 * context and make use of the macro engine to expand them.
 * <p>
 * See {@link com.zenterio.jenkins.scriptlet.BaseScriptlet} for code example.
 */
package com.zenterio.jenkins.scriptlet
