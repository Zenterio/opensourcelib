package com.zenterio.jenkins.models.job.flowdsl

class BuildFlowDslRendererTestWithParameters extends GroovyTestCase {

    BuildFlowDslRenderer dsl
    BuildFlowDslNode root

    @Override
    void setUp() throws Exception {
        BuildFlowDslParameter[] parameters = new BuildFlowDslParameter[2]
        parameters[0] = new BuildFlowDslParameter("numeric", "1")
        parameters[1] = new BuildFlowDslParameter("string", "\"value\"")
        this.dsl = new BuildFlowDslRenderer(parameters)
        this.root = new BuildFlowDslNode("root")
    }

    public void testRenderSingleNode() {
        BuildFlowDslNode n = new BuildFlowDslNode("N")
        root.addChild(n)
        String result = dsl.render(root)
        String expected = """\
def build_root = build;
build_N = build("N", numeric: 1, string: "value");
"""
        assert expected == result
    }

    public void testSiblingsAreParallel(){
        BuildFlowDslForkNode fork = new BuildFlowDslForkNode()
        root << fork
        fork << new BuildFlowDslNode("C1")
        fork << new BuildFlowDslNode("C2")
        String result = dsl.render(root)
        String expected ="""\
def build_root = build;
parallel(
  {
    build_C1 = build("C1", numeric: 1, string: "value");
  },{
    build_C2 = build("C2", numeric: 1, string: "value");
  }
);
"""
        assert expected == result
    }

    public void testRenderSingleNodeWithCustomParameter() {
        BuildFlowDslNode n = new BuildFlowDslNode("N")
        n.extraParameters.add(new BuildFlowDslParameter("customParam", "\"custom\""))
        root.addChild(n)
        String result = dsl.render(root)
        String expected = """\
def build_root = build;
build_N = build("N", numeric: 1, string: "value", customParam: "custom");
"""
        assert expected == result
    }
}
