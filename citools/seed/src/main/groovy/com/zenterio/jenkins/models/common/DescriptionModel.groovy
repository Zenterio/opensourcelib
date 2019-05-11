package com.zenterio.jenkins.models.common

import com.zenterio.jenkins.configuration.ContactInformationCollection
import com.zenterio.jenkins.models.ModelProperty;


class DescriptionModel extends ModelProperty {

    protected String description;

    public DescriptionModel(String description) {
        super()
        this.description = description
    }

    public String getDescription() {
        return this.description
    }

    private static String renderContactsHtml(ContactInformationCollection contacts, String heading) {
        String result = ""
        if (contacts) {
            result = """
        <p style='background: inherit'>
            ${heading}:<br/>
            <ul>
                ${
                contacts.collect { w ->
                    "<li><a href='mailto:${w.email}'>${w.name}</a></li>"
                }.join('\n                ')
            }
            </ul>
        </p>"""
        }
        return result
    }

    public static String renderWatchersHtml(ContactInformationCollection watchers) {
        return renderContactsHtml(watchers, "Additional watchers")
    }

    public static String renderOwnersHtml(ContactInformationCollection owners) {
        return renderContactsHtml(owners, "Owner(s)")
    }
}
