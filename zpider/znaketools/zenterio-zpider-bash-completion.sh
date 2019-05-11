#!/usr/bin/env bash
_zpider_completion() {
    COMPREPLY=( $( env COMP_WORDS="${COMP_WORDS[*]}" \
                   COMP_CWORD=$COMP_CWORD \
                   _ZPIDER_COMPLETE=complete $1 ) )
    return 0
}

complete -F _zpider_completion -o default zpider;