#!/usr/bin/env bash
_zdeb_packer_completion() {
    COMPREPLY=( $( env COMP_WORDS="${COMP_WORDS[*]}" \
                   COMP_CWORD=$COMP_CWORD \
                   _ZDEB_PACKER_COMPLETE=complete $1 ) )
    return 0
}

complete -F _zdeb_packer_completion -o default zdeb-packer;