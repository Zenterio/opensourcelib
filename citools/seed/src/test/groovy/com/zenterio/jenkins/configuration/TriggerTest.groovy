package com.zenterio.jenkins.configuration

class TriggerTest extends GroovyTestCase {

    Trigger trigger

    public void testDefaults() {
        this.trigger = new Trigger(null, null, false, true)
        assert this.trigger.polling == null
        assert this.trigger.periodic == null
        assert this.trigger.acceptNotifyCommit == false
        assert this.trigger.enabled == true
        assert this.trigger.valid == false
    }

    public void testDisabled() {
        this.trigger = new Trigger(null, null, false, false)
        assert this.trigger.polling == null
        assert this.trigger.periodic == null
        assert this.trigger.acceptNotifyCommit == false
        assert this.trigger.enabled == false
        assert this.trigger.valid == false
    }

    public void testPolling() {
        this.trigger = new Trigger("pollexpression", null, false, true)
        assert this.trigger.polling == "pollexpression"
        assert this.trigger.periodic == null
        assert this.trigger.acceptNotifyCommit == false
        assert this.trigger.enabled == true
        assert this.trigger.valid == true
    }

    public void testPeriodic() {
        this.trigger = new Trigger(null, "period", false, true)
        assert this.trigger.polling == null
        assert this.trigger.periodic == "period"
        assert this.trigger.acceptNotifyCommit == false
        assert this.trigger.enabled == true
        assert this.trigger.valid == true
    }

    public void testAcceptNotifyCommit() {
        this.trigger = new Trigger(null, null, true, true)
        assert this.trigger.polling == ' '
        assert this.trigger.periodic == null
        assert this.trigger.acceptNotifyCommit == true
        assert this.trigger.enabled == true
        assert this.trigger.valid == true
    }

    public void testPollingAndPeriodic() {
        this.trigger = new Trigger("poll", "periodic", false, true)
        assert this.trigger.polling == "poll"
        assert this.trigger.periodic == "periodic"
        assert this.trigger.acceptNotifyCommit == false
        assert this.trigger.enabled == true
        assert this.trigger.valid == true
    }



}
