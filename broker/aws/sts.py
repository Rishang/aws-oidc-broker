import json
import urllib

#  pipi
import boto3
import requests


class AWSRoleSTS:
    def __init__(self, role_arn: str, username: str = "") -> None:
        self.role_arn = role_arn
        self.username = username

    def oidc_sts(self, jwt_token: str, duration_seconds: int = 3600) -> dict:
        """
        Returns a boto3 client for OpenID Connect STS (Security Token Service)
        """

        sts = boto3.client("sts")
        self.client = sts

        self.response = sts.assume_role_with_web_identity(
            RoleArn=self.role_arn,
            RoleSessionName=self.username or "sts-role-session",
            WebIdentityToken=jwt_token,
            DurationSeconds=duration_seconds,
        )

        self.duration_seconds = duration_seconds
        return self.response

    def generate_console_url(self, issuer: str = "example.com") -> str:
        """Generate aws console access url"""

        if self.response is None:
            raise Exception("No response from STS")
        sts_role_response = self.response

        # Step 3: Format resulting temporary credentials into JSON
        url_credentials = {}
        url_credentials["sessionId"] = sts_role_response.get("Credentials").get(
            "AccessKeyId"
        )
        url_credentials["sessionKey"] = sts_role_response.get("Credentials").get(
            "SecretAccessKey"
        )
        url_credentials["sessionToken"] = sts_role_response.get("Credentials").get(
            "SessionToken"
        )

        # expiration = sts_role_response.get('Credentials').get('Expiration')
        durtion = self.duration_seconds

        json_temp_credentials = json.dumps(url_credentials)

        # Step 4. Make request to AWS federation endpoint to get sign-in token.
        #  Construct the parameter string with
        # the sign-in action request, a 12-hour session duration,
        # and the JSON document with temporary credentials
        # as parameters.
        request_url: str = "https://signin.aws.amazon.com/federation"
        request_parameters = "?Action=getSigninToken"
        request_parameters += f"&SessionDuration={durtion}"

        def quote_plus_function(s):
            return urllib.parse.quote_plus(s)

        request_parameters += "&Session=" + quote_plus_function(json_temp_credentials)
        request_url += request_parameters

        # Returns a JSON document with a single element named SigninToken.
        _r = requests.get(request_url)
        signin_token = json.loads(_r.text)

        # Step 5: Create URL where users can use the sign-in token to sign in to
        # the console. This URL must be used within 15 minutes after the
        # sign-in token was issued.
        request_parameters = "?Action=login"
        request_parameters += f"&Issuer={issuer}"
        request_parameters += "&Destination=" + quote_plus_function(
            "https://console.aws.amazon.com/"
        )
        request_parameters += "&SigninToken=" + signin_token["SigninToken"]
        request_url = "https://signin.aws.amazon.com/federation" + request_parameters

        return request_url


def get_role(token, role: str, username: str = ""):
    """Provide aws sts role access to aws cli or console based on web identity token"""

    sts: dict = {}
    if isinstance(username, str) and username != "":
        aws_role = AWSRoleSTS(role_arn=role, username=username)
    else:
        aws_role = AWSRoleSTS(role_arn=role)
    try:
        sts["cli"] = aws_role.oidc_sts(jwt_token=token)
        sts["console"] = aws_role.generate_console_url()
        sts["expired"] = False
        return sts
    except aws_role.client.exceptions.ExpiredTokenException:
        sts["expired"] = True

    return sts
