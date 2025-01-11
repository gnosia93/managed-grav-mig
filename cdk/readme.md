cdk 이용하여 워크샵용 인프라를 구성한다. 구성 언어로는 타입 스크립트를 사용할 예정이다. 

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
$ mkdir rds && cd rds

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

    const vpc = new ec2.Vpc(this, 'RdsVpc', {
      maxAzs: 4,
      vpcName: 'RdsVpc',
      ipAddresses: ec2.IpAddresses.cidr('10.0.0.0/16'),
      natGateways: 0
    });

    const aurora = new DatabaseInstance(this, 'auroraRds', {
      vpcSubnets: {
        onePerAz: true,
        subnetType: SubnetType.PRIVATE_ISOLATED
      },
      vpc: vpc,
      port: 3306,
      databaseName: 'main',
      allocatedStorage: 20,
      instanceIdentifier,
      engine: DatabaseInstanceEngine.mysql({
        version: MysqlEngineVersion.VER_8_0
      }),
      instanceType: InstanceType.of(InstanceClass.T2, InstanceSize.LARGE)
    });

  }
}
```

#### 6. 배포하기 ####
```
$ cdk deploy 
```


## 레퍼런스 ##

* https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html
* https://aws.amazon.com/blogs/infrastructure-and-automation/use-aws-cdk-to-initialize-amazon-rds-instances/
