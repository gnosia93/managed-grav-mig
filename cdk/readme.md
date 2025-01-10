
#### 1. https://nodejs.org/ko/download 로 방문하여 node.js 를 설치한다. ####


#### 2. 설치 버전을 확인한다. ####

```
$ node -v
v22.13.0

$ npm -v
10.9.2
```

#### 3. cdk 를 설치한다. ####
```
$ sudo npm install -g aws-cdk

$ cdk --version
2.175.0 (build 703e81f) 
```

#### 4. cdk 프로젝트를 생성한다. ####
```
$ mkdir rds-gravition && cd rds-gravition

$ cdk init --language typescript
```

#### 5. 아래와 같이 코드를 수정한다. ####

[bin/rds.ts]
```
#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { RdsStack } from '../lib/rds-stack';

const app = new cdk.App();
new RdsStack(app, 'RdsStack', {
  env: { account: '<aws-account-number>', region: 'ap-northeast-2' },
});
```
 `<aws-account-number>` 값을 대상 AWS 어카운트로 수정한다. 


[lib/rds-stack.ts]
```
import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';

export class RdsStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    new ec2.Vpc(this, 'RdsVpc', {
      maxAzs: 4,
      vpcName: 'RdsVpc',
      ipAddresses: ec2.IpAddresses.cidr('10.0.0.0/16'),
      natGateways: 0
    });
  }
}

```




## 레퍼런스 ##

* https://aws.amazon.com/blogs/infrastructure-and-automation/use-aws-cdk-to-initialize-amazon-rds-instances/
