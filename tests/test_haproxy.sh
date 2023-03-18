#!/bin/bash

! curl -s 'http://localhost:8080/;csv' | awk -F, '/BACKEND/{ print $18 }' | uniq | grep DOWN
