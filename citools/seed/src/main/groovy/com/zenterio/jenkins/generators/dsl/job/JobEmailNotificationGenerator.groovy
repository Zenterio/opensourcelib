package com.zenterio.jenkins.generators.dsl.job

import com.zenterio.jenkins.configuration.ContactInformationCollection
import com.zenterio.jenkins.configuration.EmailPolicyWhen
import com.zenterio.jenkins.configuration.Owner
import com.zenterio.jenkins.configuration.ProjectManager
import com.zenterio.jenkins.configuration.TechLead
import com.zenterio.jenkins.generators.IPropertyGenerator
import com.zenterio.jenkins.models.ModelProperty
import com.zenterio.jenkins.models.job.JobEmailNotificationJenkinsReceivers
import com.zenterio.jenkins.models.job.JobEmailNotificationModel
import com.zenterio.jenkins.models.job.JobEmailNotificationPolicy

import javaposse.jobdsl.dsl.Job

/*
 * Available triggers according to
 * https://github.com/jenkinsci/job-dsl-plugin/wiki/Job-reference
 * PreBuild
 * StillUnstable
 * Fixed
 * Success
 * StillFailing
 * Improvement
 * Failure
 * Regression
 * Aborted
 * NotBuilt
 * FirstFailure
 * Unstable
 * Always
 * SecondFailure
 * FirstUnstable
 * FixedUnhealthy
 * StatusChanged
 */

class JobEmailNotificationGenerator implements IPropertyGenerator {

    public void generate(ModelProperty model, Object entity) {
        JobEmailNotificationModel m = (JobEmailNotificationModel) model
        Job job = (Job) entity

        JobEmailNotificationPolicy policyJobType = m.policy
        ProjectManager pm = m.pm
        TechLead techLead = m.techLead
        ContactInformationCollection recipients = m.watchers + m.owners
        if (pm != null)  {
            recipients += pm
        }
        if (techLead != null) {
            recipients += techLead
        }

        job.with {
            publishers {
                extendedEmail {
                    recipientList('')
                    defaultContent(getMailContent(pm, techLead, m.customContent))


                    Closure addTrigger = { context, String recipientsList,
                                           JobEmailNotificationJenkinsReceivers receivers, String overrideSubject ->

                        if (receivers.developers || receivers.culprits || receivers.requester ||
                                recipientsList.length() > 0) {
                            context({
                                recipientList(recipientsList)
                                sendTo {
                                    if (recipientsList.length() > 0) {
                                        recipientList()
                                    }
                                    if (receivers.developers) {
                                        developers()
                                    }
                                    if (receivers.requester) {
                                        requester()
                                    }
                                    if (receivers.culprits) {
                                        culprits()
                                    }
                                }
                                if (overrideSubject) {
                                    subject(overrideSubject)
                                }
                            })
                        }

                    }
                    triggers {
                        addTrigger(delegate.&failure, recipientsList(recipients, policyJobType, EmailPolicyWhen.FAILURE),
                                policyJobType.failure, null)


                        addTrigger(delegate.&unstable, recipientsList(recipients, policyJobType, EmailPolicyWhen.FAILURE),
                                policyJobType.failure, null)


                        addTrigger(delegate.&aborted, recipientsList(recipients, policyJobType, EmailPolicyWhen.FAILURE),
                                policyJobType.aborted, null)


                        addTrigger(delegate.&fixedUnhealthy, recipientsList(recipients, policyJobType, EmailPolicyWhen.FAILURE),
                                policyJobType.fixed, null)


                        addTrigger(delegate.&success, recipientsList(recipients, policyJobType, EmailPolicyWhen.SUCCESS),
                                policyJobType.success, null)


                        addTrigger(delegate.&always, recipientsList(recipients, policyJobType, EmailPolicyWhen.ALWAYS),
                                policyJobType.always, null)


                        addTrigger(
                                delegate.&always,
                                '${FILE, path="LogAnalyzerWatchers.txt", fileNotFoundMessage=""}',
                                policyJobType.never, "LogAnalyzer Watcher Notification")

                    }
                }
            }
        }
    }

    /**
     * Returns customized message if project manager and tech lead is provided.
     * @param pm Project Manager
     * @param techLead Tech Lead
     * @return Custom message or null.
     */
    static protected String getMailContent(ProjectManager pm, TechLead techLead,
            String customContent) {
        String projectInfoFooter = ""
        if (pm && techLead) {
            projectInfoFooter = """
Do you have questions regarding this product?
Tech Lead: ${techLead.name}, ${techLead.email}
Project Manager: ${pm.name}, ${pm.email}
"""
        }
        String content = ""
        if (customContent) {
            content += customContent
        }
        content += """\
\$DEFAULT_CONTENT
${projectInfoFooter}
\${FILE, path="result/LogAnalysisSummary.txt", fileNotFoundMessage=""}
"""
        return content
    }

    /**
     * Helper funtion to filter out applicable recipients and collect their email adresses.
     * @param watchers ContactInformation list with watchers, pm and tech lead.
     * @param jobPolicy
     * @param result
     * @return
     */
    static private String recipientsList(ContactInformationCollection watchers,
                                         JobEmailNotificationPolicy jobPolicy, EmailPolicyWhen result) {
        ContactInformationCollection recipients = watchers.filter(jobPolicy, result)
        return recipients.emailList.join(' ')
    }
}
