#!/bin/bash
rm -f /tmp/gh_device.log
(
  echo "" | gh auth login --web -p https -s repo,workflow > /tmp/gh_device.log 2>&1
  gh auth setup-git >> /tmp/gh_device.log 2>&1
  git push -u origin main >> /tmp/gh_device.log 2>&1
  echo "SUCCESS_PUSH_COMPLETED" >> /tmp/gh_device.log
) &
sleep 2
cat /tmp/gh_device.log
