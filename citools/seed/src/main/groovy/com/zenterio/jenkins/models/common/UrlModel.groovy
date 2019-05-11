package com.zenterio.jenkins.models.common

import com.zenterio.jenkins.models.ModelProperty


class UrlModel extends ModelProperty {

    String url;

    public UrlModel(String url) {
        this.url = url;
    }

    /**
     * Remove the beginning of the url: "/view/<Project>/" to make it match the URL provided through Jenkins variable BUILD_URL.
     */
    public String getSimpleUrl() {
        def startExpr = ~/^\/.*?\/.*?\//
        return this.url - startExpr
    }
}
