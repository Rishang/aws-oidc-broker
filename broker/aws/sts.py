import json
import urllib

#  pipi
import boto3
import requests


aws_regions = {
    "us-east-1": "N. Virginia",
    "us-east-2": "Ohio",
    "us-west-1": "N. California",
    "us-west-2": "Oregon",
    "af-south-1": "Cape Town",
    "ap-east-1": "Hong Kong",
    "ap-southeast-3": "Jakarta",
    "ap-south-1": "Mumbai",
    "ap-northeast-3": "Osaka",
    "ap-northeast-2": "Seoul",
    "ap-southeast-1": "Singapore",
    "ap-southeast-2": "Sydney",
    "ap-northeast-1": "Tokyo",
    "ca-central-1": "Central",
    "eu-central-1": "Frankfurt",
    "eu-west-1": "Ireland",
    "eu-west-2": "London",
    "eu-south-1": "Milan",
    "eu-west-3": "Paris",
    "eu-north-1": "Stockholm",
    "me-south-1": "Middle Bahrain",
}


class AWSRoleSTS:
    def __init__(
        self,
        role_arn: str,
        username: str = "",
        region: str = None,  # type: ignore
        duration_seconds: int = 3600,
    ) -> None:
        self.role_arn = role_arn
        self.username = username
        self.region = region
        self.duration_seconds = duration_seconds

    def oidc_sts(self, jwt_token: str) -> dict:
        """
        Returns a boto3 client for OpenID Connect STS (Security Token Service)
        """

        sts = boto3.client("sts")
        self.client = sts

        self.response = sts.assume_role_with_web_identity(
            RoleArn=self.role_arn,
            RoleSessionName=self.username or "sts-role-session",
            WebIdentityToken=jwt_token,
            DurationSeconds=self.duration_seconds,
        )

        if isinstance(self.region, str) or self.region in aws_regions:
            # login based on region if provided
            self.response["Region"] = self.region

        return self.response

    def generate_console_url(self, issuer: str = None) -> str:  # type: ignore
        """Generate aws console access url"""

        if issuer == None or issuer == "":
            issuer = "example.com"

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
            # login based on region if provided
            "https://console.aws.amazon.com/"
            if not isinstance(self.region, str) or self.region not in aws_regions
            else f"https://{self.region}.console.aws.amazon.com/"
        )
        request_parameters += "&SigninToken=" + signin_token["SigninToken"]
        request_url = "https://signin.aws.amazon.com/federation" + request_parameters

        return request_url


def get_role(
    token,
    role: str,
    username: str = "",
    issuer: str = None,  # type: ignore
    region: str = None,  # type: ignore
    duration_seconds: int = 3600,
):
    """Provide aws sts role access to aws cli or console based on web identity token"""

    sts: dict = {}
    if isinstance(username, str) and username != "":
        aws_role = AWSRoleSTS(
            role_arn=role,
            username=username,
            region=region,
            duration_seconds=duration_seconds,
        )
    else:
        aws_role = AWSRoleSTS(role_arn=role)
    try:
        sts["cli"] = aws_role.oidc_sts(jwt_token=token)
        sts["console"] = aws_role.generate_console_url(issuer=issuer)
        sts["expired"] = False
        return sts
    except aws_role.client.exceptions.ExpiredTokenException:
        sts["expired"] = True

    return sts
