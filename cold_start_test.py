#!/usr/bin/env python3
# coding: utf-8

import argparse
import random
import time
import os
import subprocess
import pandas as pd
from tools import (
    mb_app_activity_list, mb_app_package_list,
    gb_app_activity_list, gb_app_package_list,
    close_app, clean_file_cache, open_app,
    go_to_home_screen, package_to_name
)

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="Android 冷启动性能测试脚本")
    parser.add_argument("--rounds", type=int, default=10, help="测试轮数 (默认: 10)")
    parser.add_argument("--output", type=str, default="cold_start_results.xlsx", help="输出 Excel 文件路径 (默认: 当前目录)")
    parser.add_argument("--delay", type=int, default=3, help="负载应用启动间的等待秒数 (默认: 3 秒)")
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
    1、轻度负载(light)
    从MB-scale 应用中随机挑选五个启动并放置后台
    2、中等负载
    从MB-scale 应用中启动所有应用并放置后台
    3、重度负载
    从MB-scale 应用中启动所有应用并放置后台,然后挑选2个GB-scale应用启动后放置后台,这两个GB-scale应用不要和测试目标应用相同
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
    with open(temp_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith("TotalTime"):
                parts = line.split(":")
                if len(parts) >= 2:
                    try:
                        startup_time = int(parts[1].strip())
                    except ValueError:
                        pass
    if os.path.exists(temp_file):
        os.remove(temp_file)
    return startup_time

def main():
    args = parse_arguments()
    rounds = args.rounds
    output_file = args.output
    delay = args.delay

    raw_records = []

    for app_activity in gb_app_activity_list:
        app_pkg = app_activity.split("/")[0]
        app_name = package_to_name.get(app_pkg, app_pkg)
        print(f"==== 测试 {app_name} ({app_pkg}) ====")

        for load_type in ['light', 'medium', 'heavy']:
            print(f"-- 负载: {load_type} --")
            for r in range(1, rounds + 1):
                print(f"轮次 {r}/{rounds}: 应用={app_name}, 负载={load_type}")
                clear_background()
                preload_apps(load_type, app_activity, delay)
                print(f"启动目标应用并测量启动时间...")
                time_ms = measure_startup_time(app_activity)
                if time_ms is None:
                    print("未获取到启动时间，跳过此轮。\n")
                    continue
                print(f"启动时间: {time_ms} ms\n")
                raw_records.append({
                    'app_name': app_name,
                    'load_type': load_type,
                    'round_#': r,
                    'time(ms)': time_ms
                })
    # 将原始数据写入 DataFrame
    raw_df = pd.DataFrame(raw_records, columns=['app_name','load_type','round_#','time(ms)'])
    # 计算平均值
    summary_df = raw_df.groupby(['app_name','load_type'], as_index=False)['time(ms)'].mean()
    summary_df = summary_df.rename(columns={'time(ms)': 'avg_time(ms)'})
    summary_df['avg_time(ms)'] = summary_df['avg_time(ms)'].astype(int)

    print(f"写入 Excel: {output_file}")
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        raw_df.to_excel(writer, sheet_name='raw_data', index=False)
        summary_df.to_excel(writer, sheet_name='summary', index=False)
    print("测试完成，结果已保存。")

if __name__ == '__main__':
    main()
