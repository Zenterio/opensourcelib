#!/usr/bin/env bash

function contains () {
    local seeking=$1; shift
    local in=1
    for element; do
        if [[ $element == $seeking ]]; then
            in=0
            break
        fi
    done
    return $in
}

function _zebra_completion() {
    if contains 'make' "${COMP_WORDS[@]}" ; then
        _zenterio_abs_make_autocomplete $1
        return $?
    else
        COMPREPLY=( $( env COMP_WORDS="${COMP_WORDS[*]}" \
                       COMP_CWORD=$COMP_CWORD \
                       _ZEBRA_COMPLETE=complete $1 ) )
        return 0
    fi
}

complete -F _zebra_completion -o default zebra
