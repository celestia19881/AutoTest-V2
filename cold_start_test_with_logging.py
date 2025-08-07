#!/usr/bin/env python3
# coding: utf-8

import argparse
import random
import time
import os
import subprocess
import sys
import pandas as pd
from tools import (
    mb_app_activity_list, mb_app_package_list,
    gb_app_activity_list, gb_app_package_list,
    close_app, clean_file_cache, open_app,
    go_to_home_screen, package_to_name
)

class Tee:
    """同时输出到控制台和文件的类"""
    def __init__(self, filename, mode='w', encoding='utf-8'):
        self.file = open(filename, mode, encoding=encoding)
        self.stdout = sys.stdout
        sys.stdout = self
    
    def __del__(self):
        self.close()
    
    def close(self):
        if self.file:
            self.file.close()
        sys.stdout = self.stdout
    
    def write(self, data):
        self.file.write(data)
        self.stdout.write(data)
        self.flush()  # 确保实时写入
    
    def flush(self):
        self.file.flush()
        self.stdout.flush()

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="Android 冷启动性能测试脚本")
    parser.add_argument("--rounds", type=int, default=1, help="测试轮数 (默认: 10)")
    parser.add_argument("--output", type=str, default="cold_start_results.xlsx", 
                        help="输出 Excel 文件路径 (默认: cold_start_results.xlsx)")
    parser.add_argument("--delay", type=int, default=3, 
                        help="负载应用启动间的等待秒数 (默认: 3 秒)")
    parser.add_argument("--log", type=str, default="running_out_log.txt", 
                        help="日志文件路径 (默认: running_out_log.txt)")
    return parser.parse_args()

def clear_background():
    """清除后台应用并清空文件缓存"""
    print("清理后台应用和缓存...")
    for pkg in gb_app_package_list + mb_app_package_list:
        close_app(pkg)
    clean_file_cache()
    print("清理完成\n")

def preload_apps(load_type, target_activity, delay):
    """
    根据负载类型启动其他应用并放入后台。
    load_type: 'light', 'medium', 'heavy'
    target_activity: 当前测试的 GB 应用 activity 字符串
    delay: 启动应用之间的等待时间
    """
    apps_to_launch = []
    target_pkg = target_activity.split('/')[0]

    if load_type == 'light':
        # 轻度负载：随机5个MB-scale应用
        apps_to_launch = random.sample(mb_app_activity_list, 5)
    elif load_type == 'medium':
        # 中等负载：启动所有MB-scale应用
        apps_to_launch = list(mb_app_activity_list)
    elif load_type == 'heavy':
        # 重度负载：启动所有MB-scale + 2个不同于目标应用的GB-scale应用
        apps_to_launch = list(mb_app_activity_list)
        other_gb = [app for app in gb_app_activity_list if app.split('/')[0] != target_pkg]
        if len(other_gb) >= 2:
            apps_to_launch += random.sample(other_gb, 2)
        else:
            apps_to_launch += other_gb
    else:
        return

    print(f"预置负载 [{load_type}]，共启动 {len(apps_to_launch)} 个应用并置于后台...")
    for app in apps_to_launch:
        open_app(app, output_file=subprocess.DEVNULL)
        time.sleep(delay)
    # 回到主界面
    go_to_home_screen()
    time.sleep(1)

def measure_startup_time(activity_name):
    """启动目标应用并返回启动耗时 (ms)"""
    temp_file = "temp_startup_time.log"
    if os.path.exists(temp_file):
        os.remove(temp_file)
    open_app(activity_name, output_file=temp_file)
    startup_time = None
    try:
        with open(temp_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith("TotalTime"):
                    parts = line.split(":")
                    if len(parts) >= 2:
                        try:
                            startup_time = int(parts[1].strip())
                        except ValueError:
                            pass
    except Exception as e:
        print(f"解析启动时间失败: {e}")
    if os.path.exists(temp_file):
        os.remove(temp_file)
    return startup_time

def main():
    args = parse_arguments()
    rounds = args.rounds
    output_file = args.output
    log_file = args.log
    delay = args.delay
    
    # 设置日志记录 - 同时输出到控制台和文件
    tee = Tee(log_file)
    print(f"测试日志保存到: {log_file}")
    print(f"开始测试: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试轮数: {rounds}, 负载延迟: {delay}秒, 输出文件: {output_file}")
    
    raw_records = []
    summary_records = []

    # 遍历每个 GB-scale 应用
    for app_activity in gb_app_activity_list:
        app_pkg = app_activity.split("/")[0]
        app_name = package_to_name.get(app_pkg, app_pkg)
        print(f"\n{'='*50}")
        print(f"==== 测试 {app_name} ({app_pkg}) ====")
        print(f"{'='*50}")

        for load_type in ['light', 'medium', 'heavy']:
            print(f"\n{'-'*40}")
            print(f"-- 负载: {load_type} --")
            print(f"{'-'*40}")
            
            times = []  # 存储当前负载类型的所有测试时间
            
            for r in range(1, rounds + 1):
                print(f"\n> 轮次 {r}/{rounds}: 应用={app_name}, 负载={load_type}")
                
                # 1. 清除后台和缓存
                clear_background()
                
                # 2. 预置负载
                preload_apps(load_type, app_activity, delay)
                
                # 3. 测试目标应用启动时间
                print(f">> 启动目标应用并测量启动时间...")
                time_ms = measure_startup_time(app_activity)
                
                if time_ms is None:
                    print("!! 未获取到启动时间，跳过此轮。")
                    continue
                
                print(f">> 启动时间: {time_ms} ms")
                times.append(time_ms)
            
            # 计算当前负载类型的平均时间
            if times:
                avg_time = sum(times) / len(times)
                print(f"\n{'>'*10} 平均启动时间 ({load_type}): {avg_time:.2f} ms {'<'*10}")
                summary_records.append({
                    '应用名称': app_name,
                    '负载类型': load_type,
                    '测试次数': len(times),
                    '平均启动时间(ms)': avg_time
                })
                
                # 记录原始数据
                for i, t in enumerate(times):
                    raw_records.append({
                        '应用名称': app_name,
                        '负载类型': load_type,
                        '测试轮次': i+1,
                        '启动时间(ms)': t
                    })

    # 创建DataFrame
    raw_df = pd.DataFrame(raw_records)
    summary_df = pd.DataFrame(summary_records)

    # 导出 Excel 文件
    print(f"\n{'>'*30} 写入 Excel: {output_file} {'<'*30}")
    try:
        with pd.ExcelWriter(output_file) as writer:
            raw_df.to_excel(writer, sheet_name='原始数据', index=False)
            summary_df.to_excel(writer, sheet_name='汇总数据', index=False)
        print(">> 结果保存成功!")
    except Exception as e:
        print(f"!! 保存结果失败: {e}")
    
    # 打印测试摘要
    print("\n" + "="*60)
    print("测试摘要:")
    print(f"测试应用数量: {len(gb_app_activity_list)}")
    print(f"总测试轮次: {len(raw_records)}")
    print(f"开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"结束时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    print("\n测试完成!")
    tee.close()  # 关闭日志文件

if __name__ == '__main__':
    main()