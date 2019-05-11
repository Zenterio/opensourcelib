/**
 * @Summary
 * Display the graph reports (.png files in result/graphs)
 */
// logic wrapped in closure to avoid polluting global scope
{ it ->
    graphs = manager.build.pickArtifactManager().root().list("result/graphs/**/*.png")
    if (graphs.size() > 0) {
        def resultUrl = "artifact";
        def html = "<h2>Graphs</h2>";
        for (graph in graphs) {
            def title=org.apache.commons.io.FilenameUtils.getBaseName(graph).replace('_', ' ')
            def imgUrl = "${resultUrl}/${graph}";
            html += "<h3>${title}</h3>";
            html += "<p><a href='${imgUrl}'><img src='${imgUrl}' alt='${graph}' width='160' height='128' /></a></p>";
        }
        manager.createSummary("clipboard.png").appendText(html, false);
    }
}();
