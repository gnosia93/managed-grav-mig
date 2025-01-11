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
$ mkdir grav && cd grav

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
import * as rds from 'aws-cdk-lib/aws-rds';
import * as iam from 'aws-cdk-lib/aws-iam';

export class RdsStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    /* https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ec2-readme.html */
    const vpc = new ec2.Vpc(this, 'grav-vpc', {
      maxAzs: 3,
      vpcName: 'grav-vpc',
      ipAddresses: ec2.IpAddresses.cidr('10.0.0.0/16'),
      natGateways: 0,      
      enableDnsHostnames: true,
      enableDnsSupport: true, 
      createInternetGateway: true,

      subnetConfiguration: [
        {
          cidrMask: 24,
          name: 'grav-public',
          subnetType: ec2.SubnetType.PUBLIC,
        },
        {
          cidrMask: 24,
          name: 'grav-private',
          subnetType: ec2.SubnetType.PRIVATE_ISOLATED,
        }
      ]
    });


    const ec2SecurityGroup = new ec2.SecurityGroup(this, "grav-ec2-sg", {
      securityGroupName: "grav-ec2-sg", 
      vpc: vpc,
      allowAllOutbound: true,
      description: 'ec2 security group'
    });

    ec2SecurityGroup.addIngressRule(
      ec2.Peer.anyIpv4(),
      ec2.Port.SSH, 
      'allow ssh port inbound from anywhere'
    );

    /* ec2 - 
     * https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ec2.Instance.html 
     * https://loige.co/provision-ubuntu-ec2-with-cdk/ 
     * https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_iam.ManagedPolicy.html
     * simple system manager's role binding - AmazonSSMManagedInstanceCore
     */
    const ec2instance = new ec2.Instance(this, "grav-ec2", {
      vpc: vpc,
      instanceType: ec2.InstanceType.of(ec2.InstanceClass.COMPUTE7_INTEL, ec2.InstanceSize.XLARGE2),
      machineImage: new ec2.AmazonLinuxImage({ generation: ec2.AmazonLinuxGeneration.AMAZON_LINUX_2023 }),
      securityGroup: ec2SecurityGroup,
      associatePublicIpAddress: true,
      instanceName: 'grav-ec2-instance',
      keyPair: ec2.KeyPair.fromKeyPairAttributes(this, 'aws-kp-2', {keyPairName: 'aws-kp-2'}),
      vpcSubnets: { subnetType: ec2.SubnetType.PUBLIC },
      role: new iam.Role(this, 'grav-iam-role', {
        assumedBy: new iam.ServicePrincipal('ec2.amazonaws.com'),
        managedPolicies: [iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonSSMManagedInstanceCore')]
      })
    });


    /* security group - https://github.com/bobbyhadz/aws-cdk-security-group-example/blob/cdk-v2/lib/cdk-starter-stack.ts */
    const rdsSecurityGroup = new ec2.SecurityGroup(this, "grav-rds-sg", {
      securityGroupName: "grav-rds-sg",  
      vpc: vpc,
      allowAllOutbound: true,
      description: 'database security group'
    });

    rdsSecurityGroup.addIngressRule(
      ec2.Peer.anyIpv4(),
      ec2.Port.MYSQL_AURORA,
      'allow inbound for 3306 port'
    )

    /* https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_rds-readme.html */  
    const cluster = new rds.DatabaseCluster(this, 'grav-aurora-cluster', {
      
      clusterIdentifier: "grav-aurora-cluster",
      engine: rds.DatabaseClusterEngine.auroraMysql({ version: rds.AuroraMysqlEngineVersion.VER_3_08_0 }),
      securityGroups: [ rdsSecurityGroup ],
      enablePerformanceInsights: true, 
      
      /* 
       * To delete an RDS instance in AWS CDK without creating a backup, 
       * set the removalPolicy property of your RDS construct to cdk.RemovalPolicy.DESTROY 
       * which explicitly instructs CDK to delete the resource without retaining any backups; 
       * essentially forcing a deletion without considering existing backups. 
       */
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      
      /* https://stackoverflow.com/questions/70974077/is-there-a-way-to-set-the-default-password-while-making-rds-by-cdk */
      credentials: rds.Credentials.fromPassword("admin", cdk.SecretValue.unsafePlainText("mysql-admin")), 
      
      /*
       * db.r6i.xlarge : 4 vCPUs, 32GiB RAM, 10Gbps
       */
      writer: rds.ClusterInstance.provisioned('grav-aurora-1', {
        instanceType: ec2.InstanceType.of(ec2.InstanceClass.R6I, ec2.InstanceSize.XLARGE),
        instanceIdentifier : "grav-aurora-1",
      }),
      readers: [
        // will be put in promotion tier 1 and will scale with the writer
        rds.ClusterInstance.provisioned('grav-aurora-2', {
          instanceIdentifier: 'grav-aurora-2',
          instanceType: ec2.InstanceType.of(ec2.InstanceClass.R6I, ec2.InstanceSize.XLARGE),
        }),
        rds.ClusterInstance.provisioned('grav-aurora-3', {
          instanceIdentifier: 'grav-aurora-3',
          instanceType: ec2.InstanceType.of(ec2.InstanceClass.R6I, ec2.InstanceSize.XLARGE),
        })
      ],
      vpc: vpc,
      subnetGroup: new rds.SubnetGroup(this, 'grav-db-subnet-grp', {
        description: 'grav-db-subnet-grp',
        vpc: vpc,
      
        // the properties below are optional
        removalPolicy: cdk.RemovalPolicy.DESTROY,
        subnetGroupName: 'grav-db-subnet-grp',
        vpcSubnets: {
          onePerAz: true,
          subnetType: ec2.SubnetType.PRIVATE_ISOLATED,
        },
      })
    });

  }
}

```

#### 6. 배포하기 ####
```
$ cdk bootstrap

$ cdk deploy --require-approval never
```


## 레퍼런스 ##

* https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html
* https://www.typescriptlang.org/docs/handbook/intro.html
* https://ultimatecourses.com/blog/typescript-classes-and-constructors
* https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib-readme.html
