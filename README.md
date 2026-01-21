# 国科大自动选课  
# 国科大选课 全自动
# UCAS Automatic course selection 

**无须输入验证码，可以自动识别验证码** 基于[ddddocr](https://github.com/sml2h3/ddddocr)和[dddd_trainer](https://github.com/sml2h3/dddd_trainer)  

***目前只在非高峰时期测试过，帮助大家捡漏有人退课的课，目前还不完善，在高峰期间使用可能存在bug，需要调整sleep的时间等，<span style="color:red; font-weight:bold;">禁止恶意抢课</span>，如有bug，欢迎发起issue***


## 使用方法 
`python main.py {yourUSERNAME} {yourPASSWORD} {SUBJECTID} {COURSEID} --driverPath --noCaptcha`  
*输入的时候不需要输入`{}`*   

- yourUSERNAME 例如 zhangsan@mails.ucas.ac.cn
- PASSWORD 输入自己的sep登录密码
- SUBJECTID 学院对应的- ID，目前只可选一个学院，如需增加可以在代码中自行修改
- COURSEID 课程编码，可在学期课表或选择课程中查找
- driverPath 如果没有chrome浏览器需要下载chrome浏览器，默认路径在`C:\Program Files\Google\Chrome\Application`，根据自己路径调整，为可选参数，如果不在默认路径下，需要修改默认路径
- noCaptcha 为可选参数，有时登录界面不需要验证码，此时需要加上--noCaptcha，需要验证码时，不需要加该参数

例如，  
我的账户为zhangsan@mails.ucas.ac.cn   
密码为love1234 SUBJECTID选择计算机学院，也就是id_951， 见下面学院和id一一对应    
COURSEID，假设为081202M04002H  
driverPath，假设不在默认路径下，在`D:\Programs\Google\Chrome\Application`   
此时登录界面有验证码：  
`python main.py zhangsan@mails.ucas.ac.cn love1234 id_951 081202M04002H --driverPath D:/Programs/Google/Chrome/Application`  
如果登录界面无验证码： 
`python main.py zhangsan@mails.ucas.ac.cn love1234 id_951 081202M04002H  --noCaptcha`  
如果driverPath在默认路径下，且登录界面有验证码:  
`python main.py zhangsan@mails.ucas.ac.cn love1234 id_951 081202M04002H`  


## 1. 安装所需依赖 
`pip install -r requirements.txt -i https://pypi.douban.com/simple` 
python的版本为3.9.16  

## 2. clone本项目到本地   
`git clone https://github.com/lizhuoq/UCAS-Course-selection-script.git`

## 3.学院和- ID对应 
```
{
    "数学学院": "id_910",
    "物理学院": "id_911",
    "天文学院": "id_957",
    "化学学院": "id_912",
    "材料学院": "id_928",
    "生命学院": "id_913",
    "地球学院": "id_914",
    "资环学院": "id_921",
    "计算机学院": "id_951",
    "电子学院": "id_952",
    "工程学院": "id_958",
    "经管学院": "id_917",
    "公管学院": "id_945",
    "人文学院": "id_927",
    "马克思主义学院": "id_964",
    "外语系": "id_915",
    "中丹学院": "id_954",
    "国际学院": "id_955",
    "存济医学院": "id_959",
    "体育部": "id_946",
    "集成电路学院": "id_961",
    "未来技术学院": "id_962",
    "网络空间安全学院": "id_963",
    "心理学系": "id_968",
    "人工智能学院": "id_969",
    "纳米科学与技术学院": "id_970",
    "艺术中心": "id_971",
    "光电学院": "id_972",
    "现代产业学院": "id_967",
    "核学院": "id_973",
    "现代农业科学学院": "id_974",
    "化学工程学院": "id_975",
    "海洋学院": "id_976",
    "航空宇航学院": "id_977",
    "应急管理科学与工程学院": "id_987",
    "人居科学学院": "id_989",
    "MBA": "id_950",
    "MPA": "id_965",
    "MEMEM": "id_990",
    "密码学院": "id_988",
    "前沿交叉科学学院": "id_993"
}
```

## 4.data文件和model文件
```
data/ 
|---- labels.txt
|---- images
            |----...num.png
``` 
labels 每行内容为  
num值.png\t1+1=?\n  
\t为制表符，\n为换行符 

利用[dddd_trainer](https://github.com/sml2h3/dddd_trainer)训练  
```
models/  
  |---- ocr_1.0_299_3000_2023-06-07-12-34-41.onnx 
  |---- charsets.json
```


模型权重文件在models文件夹中，识别带个位数字带运算符的验证码准确率达到99%以上  

## 5.课程编码位置 
<div  align="center">
  <img src="./temp/屏幕截图%202023-06-08%20094338.jpg" alt="img" width="100%" />
</div>
或者  
<div  align="center">
  <img src="./temp/屏幕截图%202023-06-08%20092924.jpg" alt="img" width="100%" />
</div>  