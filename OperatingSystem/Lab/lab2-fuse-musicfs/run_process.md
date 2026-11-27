## WSL环境运行：

1. 创建虚拟环境(挂载点)：`cd /mnt/d/Study-Note/OperatingSystem/Lab/lab2-fuse-musicfs`

2.  `bash run_musicfs.sh`

3. 另开终端查看：`ls -R ~/musicfs-mount`  

4. 可重复执行独立的真实音频检查：

```bash
python -m tools.check_local_audio

ls ~/musicfs-mnt
ls ~/musicfs-mnt/by_bpm
ls ~/musicfs-mnt/by_key
ls ~/musicfs-mnt/by_type
ls ~/musicfs-mnt/info

stat ~/musicfs-mnt/by_type/song/"real07__I Know.mp3"
// 检查当前实际文件信息

sha256sum ~/musicfs-mnt/by_type/song/"real07__I Know.mp3"
// 查看文件sha码

cat ~/musicfs-mnt/info/real07.info
// 查看info文件内容

// 关闭使用该目录的程序，终端退出挂载目录，然后卸载。
cd ~
fusermount3 -u ~/musicfs-mnt
```

sum commands:

• ls：列出目录内容（常用 ls -l 查看详细信息，ls -a 显示隐藏文件）。
• cd：切换工作目录（如 cd /var/log 进入指定目录，cd .. 返回上一级）。
• pwd：显示当前工作目录的绝对路径。
• mkdir：创建新目录（如 mkdir -p a/b 递归创建多级目录）。
• rmdir：删除空目录。
• cp：复制文件或目录（如 cp -r dir1 dir2 递归复制目录）。
• mv：移动文件、目录或重命名。
• rm：删除文件或目录（危险命令，加 -rf 需谨慎）。
• touch：创建空文件或修改文件时间戳。
• ln：创建软链接或硬链接（如 ln -s source.txt link.txt 创建软链接）。

二、 文件内容查看与处理

• cat：连接并一次性显示文件全部内容。
• less / more：分页或分屏查看大文件内容。
• head / tail：查看文件开头或结尾几行（常配合 -n 或 tail -f 实时追踪日志）。
• grep：文本搜索工具（如 grep "error" app.log 查找文件中匹配的关键字）。
• find：在文件系统中查找文件（如 find / -name "*.txt"）。
• diff：逐行或逐字节比较两个文件的差异。
• tar：打包与解压缩文件（如 tar -zxvf file.tar.gz 解压）。

三、 系统状态与资源监控

• top：动态实时显示系统整体负载、CPU、内存及进程占用情况。
• ps：查看当前运行的进程状态（如 ps aux 显示所有进程）。
• kill / killall：根据进程 PID 或名称发送信号终止进程（如 kill -9 <PID>）。
• df：报告文件系统磁盘空间使用情况（常用 df -h 以易读单位显示）。
• du：查看文件或目录占用的磁盘容量。
• free：显示系统内存和交换分区（swap）的使用情况。
• uname：显示系统内核与硬件架构信息（如 uname -a）。
• uptime：显示系统已运行时间、登录用户数及 1/5/15 分钟平均负载。