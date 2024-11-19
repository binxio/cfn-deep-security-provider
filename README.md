# cfn-deep-security-provider
A CloudFormation custom resource provider for managing TrendMicro DeepSecurity resources. With this Custom CloudFormation Provider you can deploy EC2 instances and DeepSecurity policies and rules from a single CloudFormation template.

The provider supports all the DeepSecurity resources of the [DeepSecurity API](https://automation.deepsecurity.trendmicro.com/article/12_5/api-reference?platform=dsaas) and provides support creating the AWS Cloud Account using the [legacy API](https://automation.deepsecurity.trendmicro.com/legacy-rest/11_3/index.html?env=dsaas#aws_accounts).

- Generic [Custom::DeepSecurity](docs/deepsecurity.md) resources like policies, rules, etc.
- [Custom::DeepSecurityAWSCloudAccount](docs/deepsecurity-aws-cloudaccount.md) for automatic AWS account synchronization
- [Custom::DeepSecurityLookup](docs/deepsecurity-lookup.md) to lookup ID's of existing resources like policies, rules, etc

### Deploy the provider
To deploy the provider, type:

```sh
aws cloudformation create-stack \
        --capabilities CAPABILITY_IAM \
        --stack-name cfn-deep-security-provider \
        --template-body file://./cloudformation/cfn-resource-provider.yaml

aws cloudformation wait stack-create-complete  --stack-name cfn-deep-security-provider
```

This CloudFormation template will use our pre-packaged provider from `463637877380.dkr.ecr.eu-central-1.amazonaws.com/xebia/cfn-deep-security-provider:1.0.0`.

### Configuring access
In order to be able to manage the DeepSecurity resources, you need to obtain create an [API key](https://help.deepsecurity.trendmicro.com/create-api-key.html) and 
store it in the parameter store under the name `/cfn-deep-security-provider/api-key`.

```
aws ssm put-parameter --name /cfn-deep-security-provider/api-key --type SecureString --value="$API_KEY"
```

In order to create the [AWS Cloud Account](docs/deepsecurity-aws-cloudaccount.md)  you need to [add an user] (https://help.deepsecurity.trendmicro.com/user-management.html?cshid=administration_users#Create_new_users_) to access the [legacy API](https://automation.deepsecurity.trendmicro.com/legacy-rest/11_3/index.html?env=dsaas#aws_accounts).
and store the username, password and tenant name in the parameter store.


```
aws ssm put-parameter --name /cfn-deep-security-provider/user --type SecureString --value="$USERNAME"
aws ssm put-parameter --name /cfn-deep-security-provider/password --type SecureString --value="$PASSWORD"
aws ssm put-parameter --name /cfn-deep-security-provider/tenant --type SecureString --value="$TENANT"
```

### Deploy the demo
In order to deploy the demo, type:

```sh
aws cloudformation create-stack \
        --capabilities CAPABILITY_NAMED_IAM \
        --stack-name cfn-deep-security-provider-demp \
        --template-body file://./cloudformation/demo.yaml

aws cloudformation wait stack-create-complete  --stack-name cfn-deep-security-provider-demo
```
