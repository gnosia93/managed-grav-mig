
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



## 레퍼런스 ##

* cdk - https://ongamedev.tistory.com/486
* vpc - https://ongamedev.tistory.com/487
* https://aws.amazon.com/blogs/infrastructure-and-automation/use-aws-cdk-to-initialize-amazon-rds-instances/
* https://github.com/aws-samples/aws-cdk-examples/tree/main/python/rds
