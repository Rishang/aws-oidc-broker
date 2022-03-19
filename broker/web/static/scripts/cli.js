
function awsCredHelper(Credentials, AssumedRoleUser) {

  const role_arn = AssumedRoleUser.Arn

  const awsVars = {
    aws_access_key_id: Credentials.AccessKeyId,
    aws_secret_access_key: Credentials.SecretAccessKey,
    aws_session_token: Credentials.SessionToken
  }

  let account_id = role_arn.split(':')[4]
  let role_name = role_arn.split(':')[5].split('/')[1]
  let profile = `[${account_id}_${role_name}]`
  let environment = {
    profile: "",
    export: { linux: "", windows: "" }
  }

  environment.account_id = account_id

  for (let v in awsVars) {
    let upper_arg = `${v}`.toUpperCase()
    let value = `${awsVars[v]}`

    profile += `\n${v}=${value}`
    environment.export.linux += `export ${upper_arg}=${value}\n`
    environment.export.windows += `SET ${upper_arg}=${value}\n`
  }

  environment.profile = profile

  return environment
}

function hljs_html(string, lang) {
  return hljs.highlight(`${string}`, { language: `${lang}` }).value
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}