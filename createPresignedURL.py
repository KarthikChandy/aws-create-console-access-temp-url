#!/usr/bin/python

import urllib, json
import requests # 'pip install requests'
from boto.sts import STSConnection

#Role should have the following trust relationship policy in place:
# {
#   "Version": "2012-10-17",
#   "Statement": [
#     {
#       "Sid": "",
#       "Effect": "Allow",
#       "Principal": {
#         "AWS": "arn:aws:iam::<YOUR_ACCOUNT_ID>:root"
#       },
#       "Action": "sts:AssumeRole",
#       "Condition": {
#         "Null": {
#           "aws:MultiFactorAuthAge": false #mfa condition is optional
#         }
#       }
#     }
#   ]
# }
# And appropriate IAM policy
roleArn = "arn:aws:iam::<YOUR_ACCOUNT_ID>:role/<NAME_OF_EXISTING_ROLE>"

###########################################
### Create preSigned URL
###########################################

# Taken from : http://docs.aws.amazon.com/STS/latest/UsingSTS/STSMgmtConsole-manualURL.html#STSConsoleLink_programPython

sts_connection = STSConnection()

assumed_role_object = sts_connection.assume_role(
    role_arn=roleArn,
    role_session_name="ConsoleSSOSession",
    duration_seconds=1800
)

# Step 3: Format resulting temporary credentials into JSON
json_string_with_temp_credentials = '{'
json_string_with_temp_credentials += '"sessionId":"' + assumed_role_object.credentials.access_key + '",'
json_string_with_temp_credentials += '"sessionKey":"' + assumed_role_object.credentials.secret_key + '",'
json_string_with_temp_credentials += '"sessionToken":"' + assumed_role_object.credentials.session_token + '"'
json_string_with_temp_credentials += '}'

# Step 4. Make request to AWS federation endpoint to get sign-in token. Pass
# the action and JSON document with temporary credentials as parameters.
request_parameters = "?Action=getSigninToken"
request_parameters += "&Session=" + urllib.quote_plus(json_string_with_temp_credentials)
request_url = "https://signin.aws.amazon.com/federation" + request_parameters
r = requests.get(request_url)

# Returns a JSON document with a single element named SigninToken.
signin_token = json.loads(r.text)

# Step 5: Create URL that will let users sign in to the console using the
# sign-in token. This URL must be used within 15 minutes of when the
# sign-in token was issued.
request_parameters = "?Action=login"
request_parameters += "&Issuer=Example.org"
request_parameters += "&Destination=" + urllib.quote_plus("https://console.aws.amazon.com/")
request_parameters += "&SigninToken=" + signin_token["SigninToken"]
request_url = "https://signin.aws.amazon.com/federation" + request_parameters

# Send final URL to stdout
print "\n\n"
print request_url
print "\n\n"
