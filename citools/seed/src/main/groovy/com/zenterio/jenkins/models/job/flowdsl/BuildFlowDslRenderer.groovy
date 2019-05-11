package com.zenterio.jenkins.models.job.flowdsl

import static com.zenterio.jenkins.Utils.safeVariableName

import com.zenterio.jenkins.models.IModel

import groovy.util.logging.*


@Log
class BuildFlowDslRenderer {

    private StringWriter out
    private IndentPrinter printer
    private BuildFlowDslParameter[] callParameters
    private BuildFlowDslVariable[] variables
    private List<IModel> delayedRendering

    public BuildFlowDslRenderer(
    BuildFlowDslParameter[] callParameters = new BuildFlowDslParameter[0],
    BuildFlowDslVariable[] variables = new BuildFlowDslVariable[0]) {

        this.callParameters = callParameters
        this.variables = variables
        this.out = new StringWriter()
        this.printer = new IndentPrinter(new PrintWriter(out), '  ')
        this.delayedRendering = new ArrayList<IModel>()
    }

    /**
     * Renders the node tree to string using the syntax
     * for Build Flow DSL. The root is not rendered as
     * it is only a place holder for the rest.
     * Siblings are built in parallel
     * Children serial to their parents
     * @param root     The root will not be rendered, holder of the
     *               rest of the tree.
     * @return        the DSL code for the build flow of the
     *                 tree as a String.
     */
    public String render(BuildFlowDslNode root) {
        log.finest("Start rendering Build Flow DSL")
        this.printLine("def build_${safeVariableName(root.jobName)} = build;")
        this.renderVariables(this.variables)
        this.renderChild(root)
        this.printer.flush()
        String result = this.out.toString()
        log.finest("End rendering Build Flow DSL")
        return result
    }

    /**
     * Renders the passed in node and all its children.
     * @param node
     * @return
     */
    protected void renderNode(BuildFlowDslNode node) {
        log.finest("Rendering (node=${node.jobName})")
        String params = this.getParamsString(node)
        this.printLine("""build_${safeVariableName(node.jobName)} = build("${node.jobName}"${params});""")
        this.renderChild(node)
    }

    /**
     * Renders the passed in node and all its children.
     * @param node
     * @return
     */
    protected void renderNode(BuildFlowDslForkNode node) {
        log.finest("Rendering fork node")
        if (node.children.size == 0) {
            // do nothing
        } else if (node.children.size == 1) {
            renderNode(node.children[0])
            this.doDelayedRendering()
        } else {
            this.printLine("""parallel(""")
            this.incrementIndent()
            this.printLine("{")
            BuildFlowDslNode last = node.children.last()
            node.children.each({ child ->
                this.incrementIndent()
                renderNode(child)
                this.decrementIndent()
                if (child != last) {
                    this.printLine("},{")
                } else {
                    this.printLine("}")
                }
            })
            this.decrementIndent()
            this.printLine(");")
            this.doDelayedRendering()
        }
    }

    /**
     * Renders the passed in join node.
     * @param joinNode
     */
    protected void renderNode(BuildFlowDslJoinNode node) {
        log.finest("Scheduling join node for delayed rendering")
        if (!this.delayedRendering.contains(node)) {
            this.delayedRendering.push(node)
        }
    }

    /**
     * Perform rendering of node top of the delayed stack
     */
    protected void doDelayedRendering() {
        log.finest("Do delayed rendering")
        if (this.delayedRendering.size > 0) {
            IModel node = this.delayedRendering.pop()
            if (node.children.size > 0) {
                this.renderNode(node.children[0])
            }
        }
    }

    protected void renderChild(IModel node) {
        if (node.children.size == 1) {
            this.renderNode(node.children[0])
        } else if (node.children.size > 1) {
            throw new BuildFlowDslRenderException(
            "Inconsistent node tree, regular node has multiple children which is not allowed. Use fork.")
        }
    }

    /**
     * Parameters properly formated in the DSL syntax
     * @param node
     * @return DSL parameter code as String
     */
    protected String getParamsString(BuildFlowDslNode node) {
        List<BuildFlowDslParameter> paramList = new ArrayList<BuildFlowDslParameter>()
        paramList.addAll(this.callParameters)
        paramList.addAll(node.extraParameters)

        String params = paramList.collect({ param -> ", ${param}" }).join("")
        return params
    }

    /**
     * Renders the variables
     * @param variables
     */
    protected void renderVariables(BuildFlowDslVariable[] variables ) {
        variables.each({variable ->
            this.printLine("""${variable.name} = ${variable.value};""")
        })
    }

    /**
     * Wrapper function to isolate the implementation of the
     * indentation mechanism used. Writes the provided string and ends
     * with newline.
     * @param line
     */
    protected void printLine(String line) {
        this.printIndent()
        this.printer.println(line)
    }

    /**
     * Wrapper function to isolate the implementation of the
     * indentation mechanism used. Writes the provided string without adding
     * newline at the end and out initial indentation.
     * @param text
     */
    protected void print(String text) {
        this.printer.print(text)
    }

    /**
     * Wrapper function to isolate the implementation of the
     * indentation mechanism used. Writes indentation.
     */
    protected void printIndent() {
        this.printer.printIndent()
    }

    /**
     * Wrapper function to isolate the implementation of the
     * indentation mechanism used. Increments the indentation used
     * for printLine().
     */
    protected void incrementIndent() {
        this.printer.incrementIndent()
    }

    /**
     * Wrapper function to isolate the implementation of the
     * indentation mechanism used. Decrements the indentation used
     * for printLine().
     */
    protected void decrementIndent() {
        this.printer.decrementIndent()
    }

    public class BuildFlowDslRenderException extends Exception {
    }
}
