package com.zenterio.jenkins.configuration

public enum CsvDataPlotStyle {
    AREA("area"),
    BAR("bar"),
    BAR3D("bar3d"),
    LINE("line"),
    LINE3D("line3d"),
    STACKEDAREA("stackedArea"),
    STACKEDBAR("stackedbar"),
    STACKEDBAR3D("stackedbar3d"),
    WATERFALL("waterfall")

    final private String style

    private CsvDataPlotStyle(String style) {
        this.style = style
    }

    @Override
    public String toString() {
        return this.style
    }

    public static CsvDataPlotStyle getFromString(String style) {
        return style?.toUpperCase() as CsvDataPlotStyle
    }
}
