#!/usr/bin/env bash
_zchangelog_completion() {
    COMPREPLY=( $( env COMP_WORDS="${COMP_WORDS[*]}" \
                   COMP_CWORD=$COMP_CWORD \
                   _ZCHANGELOG_COMPLETE=complete $1 ) )
    return 0
}

complete -F _zchangelog_completion -o default zchangelog;