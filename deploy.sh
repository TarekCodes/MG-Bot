#!/bin/bash
scp -i /c/dev/personal.pem -r mgbot.py ec2-user@ec2-13-59-18-47.us-east-2.compute.amazonaws.com:/home/ec2-user/mgbot
scp -i /c/dev/personal.pem -r dynamo.py ec2-user@ec2-13-59-18-47.us-east-2.compute.amazonaws.com:/home/ec2-user/mgbot
scp -i /c/dev/personal.pem -r config.py ec2-user@ec2-13-59-18-47.us-east-2.compute.amazonaws.com:/home/ec2-user/mgbot
scp -i /c/dev/personal.pem -r cogs ec2-user@ec2-13-59-18-47.us-east-2.compute.amazonaws.com:/home/ec2-user/mgbot/
