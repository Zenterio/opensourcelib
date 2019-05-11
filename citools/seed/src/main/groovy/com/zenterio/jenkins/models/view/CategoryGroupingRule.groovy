package com.zenterio.jenkins.models.view


class CategoryGroupingRule {
    String RegexCategorization
    String NamingRule

    public CategoryGroupingRule(String regexCategorization, String namingRule) {
        super();
        RegexCategorization = regexCategorization;
        NamingRule = namingRule;
    }
}
