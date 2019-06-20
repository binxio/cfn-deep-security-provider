# Custom::DeepSecurityLookup resource provider
The `Custom::DeepSecurityLookup` resource provider looks up the ID of existing resources from the [Deep Security](https://automation.deepsecurity.trendmicro.com/) API.

## Syntax
To lookup a DeepSecurity resource id using your your AWS CloudFormation template, use the following syntax:

```yaml
  Client:
    Type: Custom::DeepSecurityLookup
    Properties:
      Type: String
      Name: String
      Search: Object
      Connection:
        URL: 'https://app.deepsecurity.trendmicro.com/api'
        ApiKeyParameterName: '/cfn-deep-security-provider/api_key'

      ServiceToken: !Sub 'arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:cfn-deep-security-provider'
```
## Type
The name of the type to lookup in singular form. eg Policy, Rule, ComputerGroup etc.


## Search
The search criteria to lookup the object as defined by deep security /search api for specified type. It depends on the type,
but normally it looks something like this:

```yaml
maxItems: 0
searchCriteria:
  - fieldName: string
    booleanTest: true
    numericTest: less-than
    numericValue: 0
    stringTest: equal
    stringValue: string
    stringWildcards: true
    choiceTest: equal
    choiceValue: string
    firstDateValue: 0
    firstDateInclusive: true
    lastDateValue: 0
    lastDateInclusive: true
    nullTest: true
    idValue: 0
    idTest: less-than
sortByObjectID: true
```

## Name
of the resource to lookup.  This is a shorthand notation for: 
```yaml
Search: 
  maxItems: 0
  searchCriteria:
      fieldName: name
      stringValue: Name
```

## Example
to lookup the ID of the base policy, use:

```yaml
  LinuxServerPolicy:
    Type: Custom::DeepSecurityLookup
    Properties:
      Type: Policy
      Name: Linux Server
```

## Connection
In order to be able to manage the DeepSecurity resources, you need to obtain create an [API key](https://help.deepsecurity.trendmicro.com/create-api-key.html) and 
store it in the parameter store  under the name specified `ApiKeyParameterName`.

```
aws ssm put-parameter --name /cfn-deep-security-provider/api-key --type SecureString --value="$API_KEY"
```
If you store these credentials in a different location, please specify the correct parameter names.

## Return
The search will return the ID of the search result, if precisely 1 result was found.
