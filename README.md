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

This CloudFormation template will use our pre-packaged provider from `s3://binxio-public/lambdas/cfn-deep-security-provider-latest.zip`.

