#!/bin/bash

! curl -s 'http://localhost/haproxy/;csv' | awk -F, '/BACKEND/{ print $18 }' | uniq | grep DOWN
