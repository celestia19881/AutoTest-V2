任务目标：
写一个自动化的应用启动性能测试脚本

测试对象：GB-scale应用的冷启动性能
测试核心方法
tools.py文件中的open_app(activity_name,output_file=None)
方法，可以打开应用并输出应用的时间至指定的output_file
测试步骤：
步骤一：清除后台
1.1	通过close_app(package_name)关闭所有后台应用，即遍历关闭GB-scale和MB-scale应用
1.2	通过clean_file_cache()方法清除所有文件缓存
步骤二：预置负载
需要设置三种不同的负载类型，每种负载如下：
1、	轻度负载
从MB-scale 应用中随机挑选五个启动并放置后台

2、	中等负载
从MB-scale 应用中启动所有应用并放置后台

3、	重度负载
从MB-scale 应用中启动所有应用并放置后台，并挑选2个GB-scale应用启动后放置后台，这两个GB-scale应用不要和测试目标应用相同

步骤三：测试应用
通过open_app(activity_name,output_file=None)打开目标GB-scale应用并记录时间
步骤四：数据归档
每个GB-scale应用的每种负载需要测试十次，求时间的平均值
建议保留原始数据，汇总为excel（这步麻烦的话可以手动汇总）
