#!/usr/bin/env bash
_zit_completion() {
    COMPREPLY=( $( env COMP_WORDS="${COMP_WORDS[*]}"                        COMP_CWORD=$COMP_CWORD                        _ZIT_COMPLETE=complete $1 ) )
    return 0
}

complete -F _zit_completion -o default zit;