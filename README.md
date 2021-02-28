# Hermoor
Reports Valheim server stats to Cloudwatch

This currently finds the Valheim server by querying for an EC2 instance tagged with "hermoor".  In theory, it just needs any IP.

Currently only reports the player count, so we know not to shut the server down and kick people off.
