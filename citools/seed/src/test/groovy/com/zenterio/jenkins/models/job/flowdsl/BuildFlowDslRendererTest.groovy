package com.zenterio.jenkins.models.job.flowdsl

class BuildFlowDslRendererTest extends GroovyTestCase {

    BuildFlowDslRenderer dsl
    BuildFlowDslNode root

    @Override
    void setUp() throws Exception {
        this.dsl = new BuildFlowDslRenderer()
        this.root = new BuildFlowDslNode("root")
    }

    public void testRenderSingleNode() {
        root << new BuildFlowDslNode("N")
        String result = dsl.render(root)
        String expected = """\
def build_root = build;
build_N = build("N");
"""
        assert expected == result
    }

    public void testRenderSingleNodeWithDangerousCharInName() {
        root << new BuildFlowDslNode("N-1 #")
        String result = dsl.render(root)
        String expected = """\
def build_root = build;
build_N_1 = build("N-1 #");
"""
        assert expected == result
    }

    public void testRenderThrowsExceptionIfJobNodeHasMultipleChildren() {
        root << new BuildFlowDslNode("A1")
        root << new BuildFlowDslNode("AB")
        shouldFail({ dsl.render(root) })
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
    build_C1 = build("C1");
  },{
    build_C2 = build("C2");
  }
);
"""
        assert expected == result
    }

    public void testParentChildIsSerial(){
        BuildFlowDslNode p = new BuildFlowDslNode("P")
        BuildFlowDslNode c = new BuildFlowDslNode("C")
        p.addChild(c)
        root.addChild(p)
        String result = dsl.render(root)
        String expected = """\
def build_root = build;
build_P = build("P");
build_C = build("C");
"""
        assert expected == result
    }

    /**
     * Tests that parent -> child -> grand-child is serial.
     *  P
     *  |
     *  C
     *  |
     *  GC
     */
    public void testParentChildGrandChildIsSerial(){
        BuildFlowDslNode p = new BuildFlowDslNode("P")
        BuildFlowDslNode c = new BuildFlowDslNode("C")
        BuildFlowDslNode gc = new BuildFlowDslNode("GC")
        p.addChild(c)
        c.addChild(gc)
        root.addChild(p)
        String result = dsl.render(root)
        String expected = """\
def build_root = build;
build_P = build("P");
build_C = build("C");
build_GC = build("GC");
"""
        assert expected == result
    }

    /**
     * Tests that nesting with multiple children
     * is rendered correctly. A binary tree with, depth three,
     * with some nodes intentionally missing (<>).
     *                        root
     *                  /            \
     *                A                B
     *             /     \          /     \
     *           AA       AB      BA       BB
     *          /  \     /  \    /  \     /  \
     *        AAA  AAB  <>  <>  BAA  <> BBA  BBB
     */
    public void testFullBinaryTreeDept3(){
        BuildFlowDslForkNode rootFork = new BuildFlowDslForkNode()
        BuildFlowDslForkNode aFork = new BuildFlowDslForkNode()
        BuildFlowDslForkNode bFork = new BuildFlowDslForkNode()
        BuildFlowDslForkNode aaFork = new BuildFlowDslForkNode()
        BuildFlowDslForkNode bbFork = new BuildFlowDslForkNode()
        BuildFlowDslNode a = new BuildFlowDslNode("A")
        BuildFlowDslNode aa = new BuildFlowDslNode("AA")
        BuildFlowDslNode aaa = new BuildFlowDslNode("AAA")
        BuildFlowDslNode aab = new BuildFlowDslNode("AAB")
        BuildFlowDslNode ab = new BuildFlowDslNode("AB")
        a << aFork
        aFork << aa << aaFork
        aFork << ab
        aaFork << aaa
        aaFork <<aab

        BuildFlowDslNode b = new BuildFlowDslNode("B")
        BuildFlowDslNode ba = new BuildFlowDslNode("BA")
        BuildFlowDslNode baa = new BuildFlowDslNode("BAA")
        BuildFlowDslNode bb = new BuildFlowDslNode("BB")
        BuildFlowDslNode bba = new BuildFlowDslNode("BBA")
        BuildFlowDslNode bbb = new BuildFlowDslNode("BBB")
        b << bFork
        bFork << ba << baa
        bFork << bb << bbFork
        bbFork << bba
        bbFork << bbb

        root << rootFork
        rootFork << a
        rootFork << b

        String result = dsl.render(root)
        String expected = """\
def build_root = build;
parallel(
  {
    build_A = build("A");
    parallel(
      {
        build_AA = build("AA");
        parallel(
          {
            build_AAA = build("AAA");
          },{
            build_AAB = build("AAB");
          }
        );
      },{
        build_AB = build("AB");
      }
    );
  },{
    build_B = build("B");
    parallel(
      {
        build_BA = build("BA");
        build_BAA = build("BAA");
      },{
        build_BB = build("BB");
        parallel(
          {
            build_BBA = build("BBA");
          },{
            build_BBB = build("BBB");
          }
        );
      }
    );
  }
);
"""
        assert expected == result
    }

    /**
     * Tests simple join
     *   root
     *   / \
     *  A1   A2
     *   \ /
     *    B
     */
    public void testSimpleJoin() {
        BuildFlowDslForkNode fork = new BuildFlowDslForkNode()
        BuildFlowDslNode a1 = new BuildFlowDslNode("A1")
        BuildFlowDslNode a2 = new BuildFlowDslNode("A2")
        BuildFlowDslNode b = new BuildFlowDslNode("B")
        BuildFlowDslJoinNode join = new BuildFlowDslJoinNode()
        root << fork
        fork << a1 << join << b
        fork << a2 << join

        String result = dsl.render(root)
        String expected ="""\
def build_root = build;
parallel(
  {
    build_A1 = build("A1");
  },{
    build_A2 = build("A2");
  }
);
build_B = build("B");
"""
        assert expected == result
    }

    /**
     * Tests partial join
     *    root
     *   / \  \
     *  A1  A2 A3
     *   \ /
     *    B
     */
    public void testPartialJoin() {
        BuildFlowDslForkNode rootFork = new BuildFlowDslForkNode()
        BuildFlowDslForkNode subFork = new BuildFlowDslForkNode()
        BuildFlowDslNode a1 = new BuildFlowDslNode("A1")
        BuildFlowDslNode a2 = new BuildFlowDslNode("A2")
        BuildFlowDslNode a3 = new BuildFlowDslNode("A3")
        BuildFlowDslNode b = new BuildFlowDslNode("B")
        BuildFlowDslJoinNode join = new BuildFlowDslJoinNode()
        root << rootFork << subFork
        subFork << a1 << join << b
        subFork << a2 << join
        rootFork << a3

        String result = dsl.render(root)
        String expected ="""\
def build_root = build;
parallel(
  {
    parallel(
      {
        build_A1 = build("A1");
      },{
        build_A2 = build("A2");
      }
    );
    build_B = build("B");
  },{
    build_A3 = build("A3");
  }
);
"""
        assert expected == result
    }

    /**
     * Tests nested joins
     *      root
     *   /  \  \
     *  A1  A2 A3
     *   \  /  |
     *    B   /
     *     \ /
     *      C
     */
    public void testNestedJoin() {
        BuildFlowDslForkNode rootFork = new BuildFlowDslForkNode()
        BuildFlowDslForkNode subFork = new BuildFlowDslForkNode()
        BuildFlowDslNode a1 = new BuildFlowDslNode("A1")
        BuildFlowDslNode a2 = new BuildFlowDslNode("A2")
        BuildFlowDslNode a3 = new BuildFlowDslNode("A3")
        BuildFlowDslNode b = new BuildFlowDslNode("B")
        BuildFlowDslNode c = new BuildFlowDslNode("C")
        BuildFlowDslJoinNode bJoin = new BuildFlowDslJoinNode()
        BuildFlowDslJoinNode cJoin = new BuildFlowDslJoinNode()
        root << rootFork << subFork
        rootFork << a3
        subFork << a1 << bJoin << b
        subFork << a2 << bJoin
        b << cJoin << c
        a3 << cJoin

        String result = dsl.render(root)
        String expected ="""\
def build_root = build;
parallel(
  {
    parallel(
      {
        build_A1 = build("A1");
      },{
        build_A2 = build("A2");
      }
    );
    build_B = build("B");
  },{
    build_A3 = build("A3");
  }
);
build_C = build("C");
"""
        assert expected == result
    }

    /**
     * Tests chained joins
     *   root
     *   / \
     *  A1  A2
     *   \ /
     *    o
     *   / \
     *  B1  B2
     *   \ /
     *    C
     */
    public void testChainedJoins() {
        BuildFlowDslForkNode rootFork = new BuildFlowDslForkNode()
        BuildFlowDslForkNode bFork = new BuildFlowDslForkNode()
        BuildFlowDslNode a1 = new BuildFlowDslNode("A1")
        BuildFlowDslNode a2 = new BuildFlowDslNode("A2")
        BuildFlowDslNode b1 = new BuildFlowDslNode("B1")
        BuildFlowDslNode b2 = new BuildFlowDslNode("B2")
        BuildFlowDslNode c = new BuildFlowDslNode("C")
        BuildFlowDslJoinNode bJoin = new BuildFlowDslJoinNode()
        BuildFlowDslJoinNode cJoin = new BuildFlowDslJoinNode()
        root << rootFork
        rootFork << a1 << bJoin
        rootFork << a2 << bJoin
        bJoin << bFork
        bFork << b1 << cJoin << c
        bFork << b2 << cJoin

        String result = dsl.render(root)
        String expected ="""\
def build_root = build;
parallel(
  {
    build_A1 = build("A1");
  },{
    build_A2 = build("A2");
  }
);
parallel(
  {
    build_B1 = build("B1");
  },{
    build_B2 = build("B2");
  }
);
build_C = build("C");
"""
        assert expected == result
    }

    /**
     * Tests long joins
     *   root
     *   / \
     *  A1  A2
     *   |  |
     *  B1  B2
     *   \ /
     *    C
     */
    public void testLongJoins() {
        BuildFlowDslForkNode rootFork = new BuildFlowDslForkNode()
        BuildFlowDslNode a1 = new BuildFlowDslNode("A1")
        BuildFlowDslNode a2 = new BuildFlowDslNode("A2")
        BuildFlowDslNode b1 = new BuildFlowDslNode("B1")
        BuildFlowDslNode b2 = new BuildFlowDslNode("B2")
        BuildFlowDslNode c = new BuildFlowDslNode("C")
        BuildFlowDslJoinNode cJoin = new BuildFlowDslJoinNode()
        root << rootFork
        rootFork << a1 << b1 << cJoin << c
        rootFork << a2 << b2 << cJoin

        String result = dsl.render(root)
        String expected ="""\
def build_root = build;
parallel(
  {
    build_A1 = build("A1");
    build_B1 = build("B1");
  },{
    build_A2 = build("A2");
    build_B2 = build("B2");
  }
);
build_C = build("C");
"""
        assert expected == result
    }

    /**
     * Tests partial join but with incorrect forking
     *    root
     *   / \  \
     *  A1  A2 A3
     *   \ /
     *    B
     */
    public void testPartialJoinWithIncorrectForkingDoesNotThrowErrorInsteadRendersIncorrectly() {
        BuildFlowDslForkNode rootFork = new BuildFlowDslForkNode()
        BuildFlowDslNode a1 = new BuildFlowDslNode("A1")
        BuildFlowDslNode a2 = new BuildFlowDslNode("A2")
        BuildFlowDslNode a3 = new BuildFlowDslNode("A3")
        BuildFlowDslNode b = new BuildFlowDslNode("B")
        BuildFlowDslJoinNode join = new BuildFlowDslJoinNode()
        root << rootFork
        rootFork << a1 << join << b
        rootFork << a2 << join
        rootFork << a3

        String result = dsl.render(root)
        String expected ="""\
def build_root = build;
parallel(
  {
    build_A1 = build("A1");
  },{
    build_A2 = build("A2");
  },{
    build_A3 = build("A3");
  }
);
build_B = build("B");
"""
        assert expected == result
    }

    /**
     * Forks and joins without effects are no-ops.
     * The rest of the tree is still rendered.
     *
     *    root
     *      |
     *    fork
     *      |
     *    join
     *      |
     *      A
     *
     */
    public void testForkAndJoinWithoutEffectIsNoOp() {
        BuildFlowDslForkNode rootFork = new BuildFlowDslForkNode()
        BuildFlowDslNode a = new BuildFlowDslNode("A")
        BuildFlowDslJoinNode join = new BuildFlowDslJoinNode()
        root << rootFork
        rootFork << join << a
        String result = dsl.render(root)
        String expected = """\
def build_root = build;
build_A = build("A");
"""
    }

}
