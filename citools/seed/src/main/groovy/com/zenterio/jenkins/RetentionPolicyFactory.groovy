package com.zenterio.jenkins

class RetentionPolicyFactory {

    public static RetentionPolicy create(RetentionPolicyType type, Boolean saveArtifacts) {
        return new RetentionPolicy(type, saveArtifacts)
    }

    public static RetentionPolicy createIncrementalPolicy() {
        return RetentionPolicyFactory.create(RetentionPolicyType.LONG, false)
    }
}
