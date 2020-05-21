#!/usr/bin/env bash

# as much as i'd like to use python, pyyaml doesn't preserve
# order or formatting (and truly that's beyond it's scope)
# which makes for some really really ugly package.ymls
# so instead we create more problems by updating package.yml with regex
# however we _can_ use python go get the values to update

function usage() { echo "$0 <tag> <release> < package.yml > whatever.yml"; exit; }

if [[ $# != 2 ]]; then
	usage
fi

tag="$1"
release="$2"

# save whitespace, remove leading 'v' from tag
sed -r "s/(version\s+): [0-9.]+$/\1: ${tag#v}/" < /dev/stdin \
| sed -r "s/hub.git : v[0-9.]+$/hub.git : $tag/" \
| sed -r "s/(release\s+): [0-9]+$/\1: $release/"
