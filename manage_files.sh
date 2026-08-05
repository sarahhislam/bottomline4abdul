#!/bin/bash
if [ "$1" == "unlock" ]; then
    chmod -R u+w .
    xattr -rc .
    chflags -R nouchg .
    echo "🔓 Files UNLOCKED for editing."
elif [ "$1" == "lock" ]; then
    chmod -R a-w .
    chflags -R uchg .
    echo "🔒 Files LOCKED for testing."
else
    echo "Usage: ./manage_files.sh [lock|unlock]"
fi
