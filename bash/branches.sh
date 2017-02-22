#!/usr/bin/env bash

branch=`git symbolic-ref -q --short HEAD`                     # branch name if any
workorder=`git config branch.${branch:+$branch.}x-workorder`  # specific or default config
echo $workorder;
tagline="Acme-workorder-id: ${workorder:-***no workorder supplied***}"
sed -i "/^ *Acme-workorder-id:/d; \$a$tagline" "$1"