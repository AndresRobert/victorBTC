#!/usr/bin/env bash

git checkout -- .
git fetch
git branch -v -a
git switch ${1}