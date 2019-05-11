#!/usr/bin/env bash
_zk2_completion() {
    COMPREPLY=( $( env COMP_WORDS="${COMP_WORDS[*]}" \
                   COMP_CWORD=$COMP_CWORD \
                   _ZK2_COMPLETE=complete $1 ) )
    return 0
}

complete -F _zk2_completion -o default zk2;