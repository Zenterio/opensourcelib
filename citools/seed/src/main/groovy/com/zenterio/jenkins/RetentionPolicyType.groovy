package com.zenterio.jenkins

enum RetentionPolicyType {
    SHORT(10),
    MEDIUM(30),
    LONG(100),
    VERY_LONG(200),
    INFINITE(-1)

    public final int value

    private RetentionPolicyType(int value) {
        this.value = value
    }
}