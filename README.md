# multi-object-JSSP-with-lot-spliting
my graduation project

### 毕设进度
* 现阶段已完成编码解码的代码
* 下一步准备IMGA的组建、测试
* 再下一步进行多目标的实验

### push的具体方法
* step1：在gitbash中切换到本地路径
```
cd /D/TYT/Study/graduationProject/multi-object-JSSP-with-lot-spliting  # 这是本repository在本地的路径
```
* step2：检查分支，确保分支正确
```
git branch
```
* step3：将文件加入缓冲区

```
git add 文件名  # git add -A 可以上传本地项目文件夹中所有文件
```
* step4：提交修改
```
git commit -m  "修改备注" 
```
* step5：上传文件，将文件的本地改动同步到线上
```
git push origin master
```
### 创建代码库的方法
* step1：在gitbash中切换到该项目的根路径
```
cd 本地路径
```
* step2：在github个人主页上创建新repository，将其URL与上述本地路径关联起来，成功后会在指定的路径创建一个新的文件夹，就可以将新的文档放入，并push到线上
```
git clone 新repository的URL
```

### pull的具体方法
* 执行以下代码后，会自动检查线上哪些文件有哪些更新，自动把线上同步到线下
```
 git pull origin master
```

### 其他操作
* 查看当前版本库状态，标红的就是还未被线上git管理的文件，或有未同步本地改动到线上的文件，标绿的是已add的有改动的文件
```
git status
```
* 查看历史提交记录
```
git log
```
* 查看有哪些分支
```
git branch
```
* 切换分支
```
git checkout branch名  
```
