# -
该项目由py所写

打包代码：pyinstaller --onefile --noconsole 文件名字.py
安装依赖：pip install pystray pillow tkinter
安装依赖：pip install pyinstaller


功能说明：
核心功能：
倒计时关机（分钟数设置）
指定时间关机（24小时制）
立即关机
取消关机计划
每日定时关机（持久化设置）

特色功能：
安全模拟蓝屏（调用系统API实现，不影响硬件）
开机自启动配置
操作日志记录
配置自动保存（存储在AppData目录）
友好的GUI界面
高级特性：
使用系统原生API实现功能
多线程定时检查
异常处理机制
自动创建快捷方式
配置持久化存储

